# Enhanced firestore_manager.py with local storage fallback
import os
import json
import logging
import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.exceptions import NotFound, GoogleCloudError
from google.cloud.firestore_v1.base_query import FieldFilter
import functools
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("firestore_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FirestoreManager:
    """Manager for Firestore operations with local storage fallback."""

    def __init__(self, credentials_path=None, local_storage_dir=None):
        """Initialize the FirestoreManager."""
        self.credentials_path = credentials_path
        self.local_storage_dir = local_storage_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "local_storage"
        )
        self.db = None
        self.is_firestore_available = False

        # Create local storage directory if it doesn't exist
        os.makedirs(self.local_storage_dir, exist_ok=True)

        # Initialize Firestore if credentials are provided
        if credentials_path:
            self._initialize_firestore()

    def _initialize_firestore(self):
        """Initialize Firestore with error handling."""
        try:
            # Check if Firebase app is already initialized
            if not firebase_admin._apps:
                # Initialize Firebase app
                cred = credentials.Certificate(self.credentials_path)
                firebase_admin.initialize_app(cred)

            # Get Firestore client
            self.db = firestore.client()
            self.is_firestore_available = True
            logger.info("Firebase app initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing Firestore: {e}")
            self.is_firestore_available = False

    def _get_local_storage_path(self, collection, document_id=None):
        """Get the path to a local storage file."""
        collection_dir = os.path.join(self.local_storage_dir, collection)
        os.makedirs(collection_dir, exist_ok=True)
        if document_id:
            return os.path.join(collection_dir, f"{document_id}.json")
        return collection_dir

    def _save_to_local_storage(self, collection, document_id, data):
        """Save data to local storage."""
        file_path = self._get_local_storage_path(collection, document_id)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved to local storage: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving to local storage: {e}")
            return False

    def _load_from_local_storage(self, collection, document_id=None):
        """Load data from local storage."""
        if document_id:
            # Load a specific document
            file_path = self._get_local_storage_path(collection, document_id)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    logger.error(f"Error loading from local storage: {e}")
            return None
        else:
            # Load all documents in a collection
            collection_dir = self._get_local_storage_path(collection)
            results = []
            if os.path.exists(collection_dir):
                for filename in os.listdir(collection_dir):
                    if filename.endswith('.json'):
                        file_path = os.path.join(collection_dir, filename)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                document_id = filename.replace('.json', '')
                                data['id'] = document_id
                                results.append(data)
                        except Exception as e:
                            logger.error(f"Error loading from local storage: {e}")
            return results

    async def add_document(self, collection, data, document_id=None):
        """Add a document to Firestore with local storage fallback."""

        # Add timestamp
        data["timestamp"] = datetime.now().isoformat()

        # Try Firestore first
        if self.is_firestore_available:
            try:
                if document_id:
                    doc_ref = self.db.collection(collection).document(document_id)
                    await doc_ref.set(data)
                else:
                    doc_ref = self.db.collection(collection).document()
                    await doc_ref.set(data)
                    document_id = doc_ref.id
                logger.info(f"Added document to Firestore: {collection}/{document_id}")

                # Also save to local storage as backup
                self._save_to_local_storage(collection, document_id, data)
                return document_id
            except Exception as e:
                logger.error(f"Error adding document to Firestore: {e}")
                logger.info("Falling back to local storage...")
                self.is_firestore_available = False

        # Fallback to local storage
        if document_id is None:
             document_id = f"{int(time.time())}_{hashlib.md5(json.dumps(data).encode()).hexdigest()[:8]}"
        if self._save_to_local_storage(collection, document_id, data):
            return document_id

        raise Exception("Failed to add document to both Firestore and local storage")

    async def get_document(self, collection, document_id):
        """Get a document from Firestore with local storage fallback."""

        # Try Firestore first
        if self.is_firestore_available:
            try:
                doc_ref = self.db.collection(collection).document(document_id)
                doc = await doc_ref.get()
                if doc.exists:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    return data
            except Exception as e:
                logger.error(f"Error getting document from Firestore: {e}")
                logger.info("Falling back to local storage...")
                self.is_firestore_available = False

        # Fallback to local storage
        return self._load_from_local_storage(collection, document_id)
    
    async def get_collection(self, collection, query=None):
        """Get all documents in a collection with local storage fallback."""
    
        # Try Firestore first
        if self.is_firestore_available:
            try:
                collection_ref = self.db.collection(collection)
    
                # Apply query if provided
                if query:
                    for field, op, value in query:
                        collection_ref = collection_ref.where(field, op, value)
    
                docs = await collection_ref.get()
                results = []
                for doc in docs:
                    data = doc.to_dict()
                    data['id'] = doc.id  # Add document ID to the data
                    results.append(data)
                return results
            except Exception as e:
                logger.error(f"Error getting collection from Firestore: {e}")
                logger.info("Falling back to local storage...")
                self.is_firestore_available = False
    
        # Fallback to local storage
        return self._load_from_local_storage(collection)
