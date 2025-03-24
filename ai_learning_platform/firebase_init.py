"""
Firebase initialization module.

This module provides functions to initialize Firebase for the AI Learning Platform.
"""

import os
import logging
from typing import Optional
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin.exceptions import FirebaseError

logger = logging.getLogger(__name__)

_initialized = False

def initialize_firebase(credentials_path: Optional[str] = None) -> firestore.Client:
    """
    Initialize Firebase with the provided credentials.
    
    Args:
        credentials_path: Path to the Firebase credentials JSON file.
                         If None, will try to load from environment variable.
    
    Returns:
        firestore.Client: Initialized Firestore client
        
    Raises:
        ValueError: If credentials cannot be found
        firebase_admin.exceptions.FirebaseError: For Firebase-specific errors
        firestore.exceptions.FailedPrecondition: For Firestore precondition failures
        firestore.exceptions.Unavailable: When Firestore service is unavailable
        firestore.exceptions.Unauthenticated: For authentication errors
        Exception: For other initialization errors
    """
    global _initialized
    
    if _initialized:
        logger.info("Firebase already initialized, returning existing instance")
        return firestore.client()
    
    try:
        # Try to get credentials path from environment if not provided
        if not credentials_path:
            credentials_path = os.environ.get('FIREBASE_CREDENTIALS_PATH')
            
            # If still not found, try to load from config manager
            if not credentials_path:
                from ai_learning_platform.utils.config_manager import ConfigManager
                config_manager = ConfigManager()
                credentials_path = config_manager.load_firebase_config()
        
        if not credentials_path or not os.path.exists(credentials_path):
            raise ValueError(
                "Firebase credentials not found. Please provide a valid credentials path "
                "or set the FIREBASE_CREDENTIALS_PATH environment variable."
            )
        
        # Initialize Firebase app
        cred = credentials.Certificate(credentials_path)
        firebase_admin.initialize_app(cred)
        
        # Get Firestore client
        db = firestore.client()
        
        logger.info("Firebase initialized successfully")
        _initialized = True
        
        return db
    
    except ValueError as e:
        logger.error(f"Firebase initialization error (credentials): {str(e)}")
        raise
    except FirebaseError as e:
        logger.error(f"Firebase initialization error: {str(e)}")
        raise
    except firestore.exceptions.FailedPrecondition as e:
        logger.error(f"Firestore precondition failed: {str(e)}")
        raise
    except firestore.exceptions.Unavailable as e:
        logger.error(f"Firestore service unavailable: {str(e)}")
        raise
    except firestore.exceptions.Unauthenticated as e:
        logger.error(f"Firestore authentication error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during Firebase initialization: {str(e)}")
        raise