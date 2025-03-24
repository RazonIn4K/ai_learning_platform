import os
import sys
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from fastapi import FastAPI, HTTPException, Depends, status, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field

# Import FirestoreManager
from ai_learning_platform.utils.firestore_manager import FirestoreManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize FirestoreManager (will be done in startup event)
firestore_manager = None

# Initialize FastAPI app
app = FastAPI(
    title="Gray Swan Manual Testing API",
    description="API for manual testing of prompts against AI models",
    version="0.1.0",
)

@app.on_event("startup")
async def startup_event():
    global firestore_manager
    try:
        firestore_manager = await FirestoreManager(credentials_path="gen-lang-client-0374963993-firebase-adminsdk-fbsvc-1dee0c8626.json")
        logger.info("FirestoreManager initialized in startup event.")
    except Exception as e:
        logger.error(f"Failed to initialize FirestoreManager: {e}")
        sys.exit(1)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple JWT authentication for local use
SECRET_KEY = "dev_secret_key"  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Simplified user model for local use
class User(BaseModel):
    username: str
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# Hardcoded user for local development
users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("password"),
        "disabled": False,
    }
}

# Models for API requests and responses
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class PromptBase(BaseModel):
    prompt_text: str
    category: str
    techniques_used: List[str] = []
    challenge_id: Optional[str] = None
    target: Optional[str] = None
    technique: Optional[str] = None
    notes: Optional[str] = None
    status: str = "new"

class PromptCreate(PromptBase):
    pass

class Prompt(PromptBase):
    id: str
    prompt_hash: Optional[str] = None
    creation_timestamp: Optional[datetime] = None
    created_by: Optional[str] = None
    last_updated_timestamp: Optional[datetime] = None
    last_updated_by: Optional[str] = None
    version: Optional[str] = None
    filename: Optional[str] = None

class TestResultBase(BaseModel):
    prompt_id: str
    model_name: str
    model_provider: str = "gray_swan_agent"
    response: str
    success: bool
    success_score: Optional[float] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    category: Optional[str] = None
    challenge_id: Optional[str] = None

class TestResultCreate(TestResultBase):
    pass

class TestResult(TestResultBase):
    id: str
    run_id: Optional[str] = None
    creation_timestamp: Optional[datetime] = None
    created_by: Optional[str] = None
    response_time: Optional[float] = None
    response_length: Optional[int] = None
    token_usage: Optional[Dict[str, int]] = None
    error_message: Optional[str] = None


# Authentication functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Authentication endpoint
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Prompt endpoints
@app.get("/api/prompts", response_model=List[Prompt])
async def get_prompts(
    category: Optional[str] = None,
    challenge_id: Optional[str] = None,
    technique: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
):
    try:
        if challenge_id:
            prompts = await firestore_manager.get_prompts_by_challenge_id(challenge_id)
        elif category:
            prompts = await firestore_manager.get_all_prompts_for_category(category)
        # Add other retrieval methods as needed (e.g., by technique)
        else:
            prompts = await firestore_manager.get_all_prompts()  # Fetch all if no filters

        # Convert to Prompt model instances and apply pagination
        prompt_list = [Prompt(**p) for p in prompts]

         # Filter by technique if provided
        if technique:
            prompt_list = [p for p in prompt_list if technique in p.techniques_used]
        
        # Sort by creation timestamp (newest first)
        prompt_list.sort(key=lambda x: x.creation_timestamp or datetime.min, reverse=True)

        paginated_prompts = prompt_list[skip:skip+limit]
        return paginated_prompts

    except Exception as e:
        logger.error(f"Error retrieving prompts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prompts/{prompt_id}", response_model=Prompt)
async def get_prompt(
    prompt_id: str,
    current_user: User = Depends(get_current_active_user),
):
    try:
        prompt_data = await firestore_manager.get_prompt_by_id(prompt_id)
        if not prompt_data:
            raise HTTPException(status_code=404, detail="Prompt not found")
        prompt = Prompt(**prompt_data)
        return prompt
    except Exception as e:
        logger.error(f"Error retrieving prompt with ID {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/prompts", response_model=Prompt)
async def create_prompt(
    prompt: PromptCreate,
    current_user: User = Depends(get_current_active_user),
):
    prompt_id = str(uuid.uuid4())
    prompt_data = prompt.dict()
    prompt_data["id"] = prompt_id
    prompt_data["created_by"] = current_user.username
    prompt_data["creation_timestamp"] = datetime.utcnow()
    prompt_data["last_updated_timestamp"] = datetime.utcnow()
    prompt_data["last_updated_by"] = current_user.username
    prompt_data["prompt_hash"] = firestore_manager._calculate_prompt_hash(prompt.prompt_text)

    try:
        await firestore_manager.add_new_prompt(prompt_data)
        return Prompt(**prompt_data)
    except Exception as e:
        logger.error(f"Error creating prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/prompts/{prompt_id}", response_model=Prompt)
async def update_prompt(
    prompt_id: str,
    prompt_update: PromptBase,
    current_user: User = Depends(get_current_active_user),
):
    try:
        prompt_data = await firestore_manager.get_prompt_by_id(prompt_id)
        if not prompt_data:
            raise HTTPException(status_code=404, detail="Prompt not found")

        update_data = prompt_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            prompt_data[key] = value

        prompt_data["last_updated_timestamp"] = datetime.utcnow()
        prompt_data["last_updated_by"] = current_user.username
        prompt_data["prompt_hash"] = firestore_manager._calculate_prompt_hash(prompt_data["prompt_text"])

        await firestore_manager.update_prompt(prompt_id, update_data)
        return Prompt(**prompt_data)
    except Exception as e:
        logger.error(f"Error updating prompt with ID {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/prompts/{prompt_id}")
async def delete_prompt(
    prompt_id: str,
    current_user: User = Depends(get_current_active_user),
):
    try:
        await firestore_manager.delete_prompt(prompt_id)
        return {"message": "Prompt deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting prompt with ID {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Test result endpoints
@app.post("/api/results", response_model=TestResult)
async def create_test_result(
    result: TestResultCreate,
    current_user: User = Depends(get_current_active_user),
):
    prompt_data = await firestore_manager.get_prompt_by_id(result.prompt_id)
    if not prompt_data:
        raise HTTPException(status_code=404, detail="Prompt not found")

    result_id = str(uuid.uuid4())  # Generate UUID for result
    result_data = result.dict()
    result_data["id"] = result_id
    result_data["created_by"] = current_user.username
    result_data["creation_timestamp"] = datetime.utcnow()
    result_data["run_id"] = f"manual-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    # Calculate response length
    if "response" in result_data:
        result_data["response_length"] = len(result_data["response"])

    try:
        await firestore_manager.add_new_benchmark_result(result_data)

        # Update prompt status to "tested"
        prompt_data["status"] = "tested"
        prompt_data["last_updated_timestamp"] = datetime.utcnow()
        prompt_data["last_updated_by"] = current_user.username
        await firestore_manager.update_prompt(result.prompt_id, prompt_data)

        return TestResult(**result_data)
    except Exception as e:
        logger.error(f"Error creating test result: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    return TestResult(id=result_id, **result_data)

@app.get("/api/results", response_model=List[TestResult])
async def get_test_results(
    prompt_id: Optional[str] = None,
    model_name: Optional[str] = None,
    category: Optional[str] = None,
    challenge_id: Optional[str] = None,
    success: Optional[bool] = None,
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
):
    filtered_results = []
    
    for result_id, result in results_db.items():
        if prompt_id and result.get("prompt_id") != prompt_id:
            continue
        if model_name and result.get("model_name") != model_name:
            continue
        if category and result.get("category") != category:
            continue
        if challenge_id and result.get("challenge_id") != challenge_id:
            continue
        if success is not None and result.get("success") != success:
            continue
        filtered_results.append(TestResult(id=result_id, **result))
    
    # Sort by creation timestamp (newest first)
    filtered_results.sort(key=lambda x: x.creation_timestamp or datetime.min, reverse=True)
    
    # Apply pagination
    paginated_results = filtered_results[skip:skip+limit]
    
    return paginated_results

# Utility endpoints
@app.get("/api/models")
async def get_models(
    current_user: User = Depends(get_current_active_user),
):
    return {"models": models}

@app.get("/api/challenges")
async def get_challenges(
    current_user: User = Depends(get_current_active_user),
):
    return {"challenges": challenges}

@app.get("/api/categories")
async def get_categories(
    current_user: User = Depends(get_current_active_user),
):
    return {"categories": categories}

@app.get("/api/techniques")
async def get_techniques(
    current_user: User = Depends(get_current_active_user),
):
    return {"techniques": techniques}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Gray Swan Manual Testing API"}