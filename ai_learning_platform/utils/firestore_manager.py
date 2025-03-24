import asyncio
import hashlib
import logging
from typing import Optional

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.exceptions import NotFound, GoogleCloudError
import functools
import time

from ai_learning_platform.utils.config_manager import ConfigManager


_config_manager = ConfigManager()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def retry(max_retries=3, initial_delay=1, backoff=2):
    """Retry decorator with exponential backoff."""

    def decorator_retry(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            delay = initial_delay
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except GoogleCloudError as e:
                    retries += 1
                    logging.error(f"Attempt {retries} failed: {e}. Retrying in {delay} seconds...")
                    if retries == max_retries:
                        logging.error(f"Max retries reached for {func.__name__}. Aborting.")
                        raise  # Re-raise the exception after max retries
                    await asyncio.sleep(delay)
                    delay *= backoff  # Exponential backoff
                except Exception as e:
                    logging.error(f"An unexpected error occurred in {func.__name__}: {e}")
                    raise  # Re-raise the exception for unexpected errors

        return wrapper

    return decorator_retry


class FirestoreManager:
    """
    A class to encapsulate helper functions for interacting with Firestore.
    """

    def __init__(self, credentials_path: str):
        """
        Initializes the FirestoreManager with the path to the Firebase credentials.

        Args:
            credentials_path (str): The path to the Firebase service account credentials JSON file.
        """
        self._config_manager = ConfigManager()
        self._credentials_path = credentials_path
        self._uid = self._config_manager.load_uid()
        self._initialize_firebase()

    async def _initialize_firebase(self):
        """
        Initializes the Firebase app using the provided credentials.
        """
        try:
            cred = credentials.Certificate(self._credentials_path)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            logging.info("Firebase app initialized successfully.")
        except FileNotFoundError:
            logging.error(f"Credentials file not found at: {self._credentials_path}")
            raise  # Re-raise the exception to indicate initialization failure

    @retry()
    async def add_new_prompt(self, prompt_data: dict) -> str:
        """
        Adds a new prompt to the 'prompts' collection in Firestore.

        Args:
            prompt_data (dict): A dictionary containing the prompt data.

        Returns:
            str: The document ID of the newly created prompt.
        """
        try:
            if "prompt_text" in prompt_data:
                prompt_hash = hashlib.sha256(prompt_data["prompt_text"].encode()).hexdigest()
                prompt_data["prompt_hash"] = prompt_hash
            prompt_data["creation_timestamp"] = firestore.SERVER_TIMESTAMP
            doc_ref = self.db.collection("prompts").document()
            await doc_ref.set(prompt_data)
            logging.info(f"Prompt added with ID: {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            logging.error(f"Error adding prompt to Firestore: {e}")
            raise

    @retry()
    async def get_prompt_by_id(self, prompt_id: str) -> Optional[dict]:
        """
        Retrieves a prompt from the 'prompts' collection in Firestore by its ID.

        Args:
            prompt_id (str): The ID of the prompt to retrieve.

        Returns:
            Optional[dict]: The prompt data as a dictionary if found, or None if not found.
        """
        try:
            doc_ref = self.db.collection("prompts").document(prompt_id)
            doc = await doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            else:
                return None
        except NotFound:
            logging.warning(f"Prompt with ID {prompt_id} not found.")
            return None
        except Exception as e:
            logging.error(f"Error getting prompt from Firestore: {e}")
            raise

    @retry()
    async def get_prompt_by_text(self, prompt_text: str) -> Optional[dict]:
        """
        Retrieves a prompt from the 'prompts' collection in Firestore by its text.

        Args:
            prompt_text (str): The text of the prompt to retrieve.

        Returns:
            Optional[dict]: The prompt data as a dictionary if found, or None if not found.
        """
        try:
            query = self.db.collection("prompts").where("prompt_text", "==", prompt_text)
            docs = await query.get()
            if not docs.empty:
                # Assuming prompt_text is unique, return the first document
                return docs[0].to_dict()
            else:
                return None
        except Exception as e:
            logging.error(f"Error getting prompt from Firestore: {e}")
            raise

    @retry()
    async def get_all_prompts_for_category(
        self,
        category: str,
        limit: int = 50,
        start_after: Optional[dict] = None,
    ) -> list[dict]:
        """
        Retrieves all prompts for a given category from the 'prompts' collection in Firestore,
        with pagination.

        Args:
            category (str): The category to filter prompts by.
            limit (int): The maximum number of prompts to retrieve. Defaults to 50.
            start_after (Optional[dict]): The document data to start the query after, for pagination. Defaults to None.

        Returns:
            list[dict]: A list of prompt data dictionaries.
        """
        try:
            query = (
                self.db.collection("prompts")
                .where("category", "==", category)
                .order_by("creation_timestamp")
                .limit(limit)
            )
            if start_after:
                query = query.start_after(start_after)
            docs = await query.get()
            prompts = [doc.to_dict() for doc in docs]
            return prompts
        except Exception as e:
            logging.error(f"Error getting prompts from Firestore: {e}")
            raise

    @retry()
    async def batch_write_prompts(self, prompt_data_list: list[dict]):
        """
        Adds a list of prompts to the 'prompts' collection in Firestore using batch writes.

        Args:
            prompt_data_list (list[dict]): A list of dictionaries, each containing prompt data.
        """
        try:
            batch = self.db.batch()
            for prompt_data in prompt_data_list:
                prompt_data["creation_timestamp"] = firestore.SERVER_TIMESTAMP
                doc_ref = self.db.collection("prompts").document()
                batch.set(doc_ref, prompt_data)
            await batch.commit()
            logging.info(f"Successfully added {len(prompt_data_list)} prompts using batch write.")
        except Exception as e:
            logging.error(f"Error adding prompts to Firestore using batch write: {e}")
            raise

    @retry()
    async def update_prompt(self, prompt_id: str, updates: dict) -> None:
        """
        Updates a prompt in the 'prompts' collection in Firestore.

        Args:
            prompt_id (str): The ID of the prompt to update.
            updates (dict): A dictionary containing the fields to update.
        """
        try:
            doc_ref = self.db.collection("prompts").document(prompt_id)
            await doc_ref.update(updates)
            logging.info(f"Prompt with ID {prompt_id} updated successfully.")
        except NotFound:
            logging.warning(f"Prompt with ID {prompt_id} not found.")
        except Exception as e:
            logging.error(f"Error updating prompt in Firestore: {e}")
            raise

    @retry()
    async def delete_prompt(self, prompt_id: str) -> None:
        """
        Deletes a prompt from the 'prompts' collection in Firestore.

        Args:
            prompt_id (str): The ID of the prompt to delete.
        """
        try:
            doc_ref = self.db.collection("prompts").document(prompt_id)
            await doc_ref.delete()
            logging.info(f"Prompt with ID {prompt_id} deleted successfully.")
        except NotFound:
            logging.warning(f"Prompt with ID {prompt_id} not found.")
        except Exception as e:
            logging.error(f"Error deleting prompt from Firestore: {e}")
            raise

    @retry()
    async def get_all_prompts_created_after(
        self,
        timestamp,
        limit: int = 50,
        start_after: Optional[dict] = None,
    ) -> list[dict]:
        """
        Retrieves all prompts created after a given timestamp from the 'prompts'
        collection in Firestore, with pagination.

        Args:
            timestamp (datetime): The timestamp to filter prompts by.
            limit (int): The maximum number of prompts to retrieve. Defaults to 50.
            start_after (Optional[dict]): The document data to start the query after, for pagination. Defaults to None.

        Returns:
            list[dict]: A list of prompt data dictionaries.
        """
        try:
            query = (
                self.db.collection("prompts")
                .where("creation_timestamp", ">", timestamp)
                .order_by("creation_timestamp")
                .limit(limit)
            )
            if start_after:
                query = query.start_after(start_after)
            docs = await query.get()
            prompts = [doc.to_dict() for doc in docs]
            return prompts
        except Exception as e:
            logging.error(f"Error getting prompts from Firestore: {e}")
            raise

    @retry()
    async def get_average_success_rate(self, model_name: str, category: str) -> Optional[float]:
        """
        Calculates the average success rate for a given model and category.

        Args:
            model_name (str): The name of the model.
            category (str): The category.

        Returns:
            Optional[float]: The average success rate, or None if no results are found.
        """
        try:
            query = (
                self.db.collection("benchmark_results")
                .where("model_name", "==", model_name)
                .where("category", "==", category)
            )
            docs = await query.get()
            if not docs.empty:
                success_rates = [doc.to_dict().get("success", False) for doc in docs]
                # Convert boolean to int for calculation (True -> 1, False -> 0)
                success_rates_int = [int(success) for success in success_rates]
                avg_success_rate = sum(success_rates_int) / len(success_rates_int)
                return avg_success_rate
            else:
                return None
        except Exception as e:
            logging.error(f"Error calculating average success rate: {e}")
            raise


    @retry()
    async def add_new_benchmark_result(self, result_data: dict) -> str:
        """
        Adds a new benchmark result to the 'benchmark_results' collection in Firestore.

        Args:
            result_data (dict): A dictionary containing the benchmark result data.

        Returns:
            str: The document ID of the newly created benchmark result.
        """
        try:
            result_data["creation_timestamp"] = firestore.SERVER_TIMESTAMP
            doc_ref = self.db.collection("benchmark_results").document()
            await doc_ref.set(result_data)
            logging.info(f"Benchmark result added with ID: {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            logging.error(f"Error adding benchmark result to Firestore: {e}")
            raise
