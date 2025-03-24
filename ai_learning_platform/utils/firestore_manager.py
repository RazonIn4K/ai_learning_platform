import asyncio
import hashlib
import logging
import uuid
from typing import Optional, List, Dict, Any, Union

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.exceptions import NotFound, GoogleCloudError
from google.cloud.firestore_v1.base_query import FieldFilter
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
                .where(filter=FieldFilter("model_name", "==", model_name))
                .where(filter=FieldFilter("category", "==", category))
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
            # Generate a run_id if not provided
            if "run_id" not in result_data:
                result_data["run_id"] = str(uuid.uuid4())
                
            result_data["creation_timestamp"] = firestore.SERVER_TIMESTAMP
            doc_ref = self.db.collection("benchmark_results").document()
            await doc_ref.set(result_data)
            logging.info(f"Benchmark result added with ID: {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            logging.error(f"Error adding benchmark result to Firestore: {e}")
            raise
            
    @retry()
    async def batch_write_results(self, result_data_list: List[Dict[str, Any]]) -> List[str]:
        """
        Adds multiple benchmark results to the 'benchmark_results' collection in Firestore using batch writes.

        Args:
            result_data_list (List[Dict[str, Any]]): A list of dictionaries, each containing benchmark result data.

        Returns:
            List[str]: The document IDs of the newly created benchmark results.
        """
        try:
            batch = self.db.batch()
            doc_refs = []
            
            for result_data in result_data_list:
                # Generate a run_id if not provided
                if "run_id" not in result_data:
                    result_data["run_id"] = str(uuid.uuid4())
                    
                result_data["creation_timestamp"] = firestore.SERVER_TIMESTAMP
                doc_ref = self.db.collection("benchmark_results").document()
                doc_refs.append(doc_ref)
                batch.set(doc_ref, result_data)
                
            await batch.commit()
            
            doc_ids = [doc_ref.id for doc_ref in doc_refs]
            logging.info(f"Successfully added {len(doc_ids)} benchmark results using batch write.")
            return doc_ids
        except Exception as e:
            logging.error(f"Error adding benchmark results to Firestore using batch write: {e}")
            raise
            
    @retry()
    async def get_prompt_by_hash(self, prompt_hash: str) -> Optional[dict]:
        """
        Retrieves a prompt from the 'prompts' collection in Firestore by its hash.

        Args:
            prompt_hash (str): The hash of the prompt to retrieve.

        Returns:
            Optional[dict]: The prompt data as a dictionary if found, or None if not found.
        """
        try:
            query = self.db.collection("prompts").where(filter=FieldFilter("prompt_hash", "==", prompt_hash))
            docs = await query.get()
            if not docs.empty:
                # Assuming prompt_hash is unique, return the first document
                doc = docs[0]
                result = doc.to_dict()
                result["id"] = doc.id  # Add the document ID to the result
                return result
            else:
                return None
        except Exception as e:
            logging.error(f"Error getting prompt from Firestore by hash: {e}")
            raise
            
    @retry()
    async def get_prompts_by_category_and_technique(
        self,
        category: str,
        technique: str,
        limit: int = 50,
        start_after: Optional[dict] = None,
    ) -> List[dict]:
        """
        Retrieves prompts from the 'prompts' collection in Firestore by category and technique.

        Args:
            category (str): The category to filter prompts by.
            technique (str): The technique to filter prompts by.
            limit (int): The maximum number of prompts to retrieve. Defaults to 50.
            start_after (Optional[dict]): The document data to start the query after, for pagination. Defaults to None.

        Returns:
            List[dict]: A list of prompt data dictionaries.
        """
        try:
            query = (
                self.db.collection("prompts")
                .where(filter=FieldFilter("category", "==", category))
                .where(filter=FieldFilter("techniques_used", "array_contains", technique))
                .limit(limit)
            )
            
            if start_after:
                query = query.start_after(start_after)
                
            docs = await query.get()
            prompts = []
            
            for doc in docs:
                prompt_data = doc.to_dict()
                prompt_data["id"] = doc.id  # Add the document ID to the result
                prompts.append(prompt_data)
                
            return prompts
        except Exception as e:
            logging.error(f"Error getting prompts from Firestore by category and technique: {e}")
            raise
            
    @retry()
    async def get_prompts_by_challenge_id(
        self,
        challenge_id: str,
        limit: int = 50,
        start_after: Optional[dict] = None,
    ) -> List[dict]:
        """
        Retrieves prompts from the 'prompts' collection in Firestore by challenge ID.

        Args:
            challenge_id (str): The challenge ID to filter prompts by.
            limit (int): The maximum number of prompts to retrieve. Defaults to 50.
            start_after (Optional[dict]): The document data to start the query after, for pagination. Defaults to None.

        Returns:
            List[dict]: A list of prompt data dictionaries.
        """
        try:
            query = (
                self.db.collection("prompts")
                .where(filter=FieldFilter("challenge_id", "==", challenge_id))
                .limit(limit)
            )
            
            if start_after:
                query = query.start_after(start_after)
                
            docs = await query.get()
            prompts = []
            
            for doc in docs:
                prompt_data = doc.to_dict()
                prompt_data["id"] = doc.id  # Add the document ID to the result
                prompts.append(prompt_data)
                
            return prompts
        except Exception as e:
            logging.error(f"Error getting prompts from Firestore by challenge ID: {e}")
            raise
            
    @retry()
    async def get_all_prompts(
        self,
        limit: int = 50,
        start_after: Optional[dict] = None,
    ) -> List[dict]:
        """
        Retrieves all prompts from the 'prompts' collection in Firestore, with pagination.

        Args:
            limit (int): The maximum number of prompts to retrieve. Defaults to 50.
            start_after (Optional[dict]): The document data to start the query after, for pagination. Defaults to None.

        Returns:
            List[dict]: A list of prompt data dictionaries.
        """
        try:
            query = (
                self.db.collection("prompts")
                .order_by("creation_timestamp")
                .limit(limit)
            )
            
            if start_after:
                query = query.start_after(start_after)
                
            docs = await query.get()
            prompts = []
            
            for doc in docs:
                prompt_data = doc.to_dict()
                prompt_data["id"] = doc.id  # Add the document ID to the result
                prompts.append(prompt_data)
                
            return prompts
        except Exception as e:
            logging.error(f"Error getting all prompts from Firestore: {e}")
            raise
            
    @retry()
    async def get_prompts_by_version_and_category(
        self,
        version: str,
        category: str,
        limit: int = 50,
        start_after: Optional[dict] = None,
    ) -> List[dict]:
        """
        Retrieves prompts from the 'prompts' collection in Firestore by Gray Swan version and category.

        Args:
            version (str): The Gray Swan version to filter prompts by.
            category (str): The category to filter prompts by.
            limit (int): The maximum number of prompts to retrieve. Defaults to 50.
            start_after (Optional[dict]): The document data to start the query after, for pagination. Defaults to None.

        Returns:
            List[dict]: A list of prompt data dictionaries.
        """
        try:
            query = (
                self.db.collection("prompts")
                .where(filter=FieldFilter("gray_swan_version", "==", version))
                .where(filter=FieldFilter("category", "==", category))
                .limit(limit)
            )
            
            if start_after:
                query = query.start_after(start_after)
                
            docs = await query.get()
            prompts = []
            
            for doc in docs:
                prompt_data = doc.to_dict()
                prompt_data["id"] = doc.id  # Add the document ID to the result
                prompts.append(prompt_data)
                
            return prompts
        except Exception as e:
            logging.error(f"Error getting prompts from Firestore by version and category: {e}")
            raise
            
    @retry()
    async def get_prompts_by_technique(
        self,
        technique: str,
        limit: int = 50,
        start_after: Optional[dict] = None,
    ) -> List[dict]:
        """
        Retrieves prompts from the 'prompts' collection in Firestore by technique.

        Args:
            technique (str): The technique to filter prompts by.
            limit (int): The maximum number of prompts to retrieve. Defaults to 50.
            start_after (Optional[dict]): The document data to start the query after, for pagination. Defaults to None.

        Returns:
            List[dict]: A list of prompt data dictionaries.
        """
        try:
            query = (
                self.db.collection("prompts")
                .where(filter=FieldFilter("techniques_used", "array_contains", technique))
                .limit(limit)
            )
            
            if start_after:
                query = query.start_after(start_after)
                
            docs = await query.get()
            prompts = []
            
            for doc in docs:
                prompt_data = doc.to_dict()
                prompt_data["id"] = doc.id  # Add the document ID to the result
                prompts.append(prompt_data)
                
            return prompts
        except Exception as e:
            logging.error(f"Error getting prompts from Firestore by technique: {e}")
            raise
            
    @retry()
    async def get_prompts_by_category_after_timestamp(
        self,
        category: str,
        timestamp,
        limit: int = 50,
        start_after: Optional[dict] = None,
    ) -> List[dict]:
        """
        Retrieves prompts from the 'prompts' collection in Firestore by category created after a timestamp.

        Args:
            category (str): The category to filter prompts by.
            timestamp: The timestamp to filter prompts by.
            limit (int): The maximum number of prompts to retrieve. Defaults to 50.
            start_after (Optional[dict]): The document data to start the query after, for pagination. Defaults to None.

        Returns:
            List[dict]: A list of prompt data dictionaries.
        """
        try:
            query = (
                self.db.collection("prompts")
                .where(filter=FieldFilter("category", "==", category))
                .where(filter=FieldFilter("creation_timestamp", ">", timestamp))
                .order_by("creation_timestamp")
                .limit(limit)
            )
            
            if start_after:
                query = query.start_after(start_after)
                
            docs = await query.get()
            prompts = []
            
            for doc in docs:
                prompt_data = doc.to_dict()
                prompt_data["id"] = doc.id  # Add the document ID to the result
                prompts.append(prompt_data)
                
            return prompts
        except Exception as e:
            logging.error(f"Error getting prompts from Firestore by category after timestamp: {e}")
            raise
            
    # Benchmark Results Collection Queries
    
    @retry()
    async def get_benchmark_results_by_prompt_id(
        self,
        prompt_id: str,
        limit: int = 50,
        start_after: Optional[dict] = None,
    ) -> List[dict]:
        """
        Retrieves benchmark results from the 'benchmark_results' collection in Firestore by prompt ID.

        Args:
            prompt_id (str): The prompt ID to filter results by.
            limit (int): The maximum number of results to retrieve. Defaults to 50.
            start_after (Optional[dict]): The document data to start the query after, for pagination. Defaults to None.

        Returns:
            List[dict]: A list of benchmark result data dictionaries.
        """
        try:
            query = (
                self.db.collection("benchmark_results")
                .where(filter=FieldFilter("prompt_id", "==", prompt_id))
                .limit(limit)
            )
            
            if start_after:
                query = query.start_after(start_after)
                
            docs = await query.get()
            results = []
            
            for doc in docs:
                result_data = doc.to_dict()
                result_data["id"] = doc.id  # Add the document ID to the result
                results.append(result_data)
                
            return results
        except Exception as e:
            logging.error(f"Error getting benchmark results from Firestore by prompt ID: {e}")
            raise
            
    @retry()
    async def get_benchmark_results_by_model(
        self,
        model_name: str,
        limit: int = 50,
        start_after: Optional[dict] = None,
    ) -> List[dict]:
        """
        Retrieves benchmark results from the 'benchmark_results' collection in Firestore by model name.

        Args:
            model_name (str): The model name to filter results by.
            limit (int): The maximum number of results to retrieve. Defaults to 50.
            start_after (Optional[dict]): The document data to start the query after, for pagination. Defaults to None.

        Returns:
            List[dict]: A list of benchmark result data dictionaries.
        """
        try:
            query = (
                self.db.collection("benchmark_results")
                .where(filter=FieldFilter("model_name", "==", model_name))
                .limit(limit)
            )
            
            if start_after:
                query = query.start_after(start_after)
                
            docs = await query.get()
            results = []
            
            for doc in docs:
                result_data = doc.to_dict()
                result_data["id"] = doc.id  # Add the document ID to the result
                results.append(result_data)
                
            return results
        except Exception as e:
            logging.error(f"Error getting benchmark results from Firestore by model name: {e}")
            raise
            
    @retry()
    async def get_benchmark_results_by_run_id(
        self,
        run_id: str,
        limit: int = 50,
        start_after: Optional[dict] = None,
    ) -> List[dict]:
        """
        Retrieves benchmark results from the 'benchmark_results' collection in Firestore by run ID.

        Args:
            run_id (str): The run ID to filter results by.
            limit (int): The maximum number of results to retrieve. Defaults to 50.
            start_after (Optional[dict]): The document data to start the query after, for pagination. Defaults to None.

        Returns:
            List[dict]: A list of benchmark result data dictionaries.
        """
        try:
            query = (
                self.db.collection("benchmark_results")
                .where(filter=FieldFilter("run_id", "==", run_id))
                .limit(limit)
            )
            
            if start_after:
                query = query.start_after(start_after)
                
            docs = await query.get()
            results = []
            
            for doc in docs:
                result_data = doc.to_dict()
                result_data["id"] = doc.id  # Add the document ID to the result
                results.append(result_data)
                
            return results
        except Exception as e:
            logging.error(f"Error getting benchmark results from Firestore by run ID: {e}")
            raise
            
    @retry()
    async def get_benchmark_results_by_model_and_category(
        self,
        model_name: str,
        category: str,
        limit: int = 50,
        start_after: Optional[dict] = None,
    ) -> List[dict]:
        """
        Retrieves benchmark results from the 'benchmark_results' collection in Firestore by model name and category.

        Args:
            model_name (str): The model name to filter results by.
            category (str): The category to filter results by.
            limit (int): The maximum number of results to retrieve. Defaults to 50.
            start_after (Optional[dict]): The document data to start the query after, for pagination. Defaults to None.

        Returns:
            List[dict]: A list of benchmark result data dictionaries.
        """
        try:
            query = (
                self.db.collection("benchmark_results")
                .where(filter=FieldFilter("model_name", "==", model_name))
                .where(filter=FieldFilter("category", "==", category))
                .limit(limit)
            )
            
            if start_after:
                query = query.start_after(start_after)
                
            docs = await query.get()
            results = []
            
            for doc in docs:
                result_data = doc.to_dict()
                result_data["id"] = doc.id  # Add the document ID to the result
                results.append(result_data)
                
            return results
        except Exception as e:
            logging.error(f"Error getting benchmark results from Firestore by model name and category: {e}")
            raise
            
    @retry()
    async def get_benchmark_results_by_prompt_model_category(
        self,
        prompt_id: str,
        model_name: str,
        category: str,
        limit: int = 50,
        start_after: Optional[dict] = None,
    ) -> List[dict]:
        """
        Retrieves benchmark results from the 'benchmark_results' collection in Firestore by prompt ID, model name, and category.

        Args:
            prompt_id (str): The prompt ID to filter results by.
            model_name (str): The model name to filter results by.
            category (str): The category to filter results by.
            limit (int): The maximum number of results to retrieve. Defaults to 50.
            start_after (Optional[dict]): The document data to start the query after, for pagination. Defaults to None.

        Returns:
            List[dict]: A list of benchmark result data dictionaries.
        """
        try:
            query = (
                self.db.collection("benchmark_results")
                .where(filter=FieldFilter("prompt_id", "==", prompt_id))
                .where(filter=FieldFilter("model_name", "==", model_name))
                .where(filter=FieldFilter("category", "==", category))
                .limit(limit)
            )
            
            if start_after:
                query = query.start_after(start_after)
                
            docs = await query.get()
            results = []
            
            for doc in docs:
                result_data = doc.to_dict()
                result_data["id"] = doc.id  # Add the document ID to the result
                results.append(result_data)
                
            return results
        except Exception as e:
            logging.error(f"Error getting benchmark results from Firestore by prompt ID, model name, and category: {e}")
            raise
            
    @retry()
    async def get_benchmark_results_by_technique_and_success(
        self,
        technique: str,
        success_status: bool,
        limit: int = 50,
        start_after: Optional[dict] = None,
    ) -> List[dict]:
        """
        Retrieves benchmark results from the 'benchmark_results' collection in Firestore by technique and success status.

        Args:
            technique (str): The technique to filter results by.
            success_status (bool): The success status to filter results by.
            limit (int): The maximum number of results to retrieve. Defaults to 50.
            start_after (Optional[dict]): The document data to start the query after, for pagination. Defaults to None.

        Returns:
            List[dict]: A list of benchmark result data dictionaries.
        """
        try:
            query = (
                self.db.collection("benchmark_results")
                .where(filter=FieldFilter("technique", "==", technique))
                .where(filter=FieldFilter("success", "==", success_status))
                .limit(limit)
            )
            
            if start_after:
                query = query.start_after(start_after)
                
            docs = await query.get()
            results = []
            
            for doc in docs:
                result_data = doc.to_dict()
                result_data["id"] = doc.id  # Add the document ID to the result
                results.append(result_data)
                
            return results
        except Exception as e:
            logging.error(f"Error getting benchmark results from Firestore by technique and success status: {e}")
            raise
            
    @retry()
    async def get_benchmark_results_by_version_and_model(
        self,
        version: str,
        model_name: str,
        limit: int = 50,
        start_after: Optional[dict] = None,
    ) -> List[dict]:
        """
        Retrieves benchmark results from the 'benchmark_results' collection in Firestore by Gray Swan version and model name.

        Args:
            version (str): The Gray Swan version to filter results by.
            model_name (str): The model name to filter results by.
            limit (int): The maximum number of results to retrieve. Defaults to 50.
            start_after (Optional[dict]): The document data to start the query after, for pagination. Defaults to None.

        Returns:
            List[dict]: A list of benchmark result data dictionaries.
        """
        try:
            query = (
                self.db.collection("benchmark_results")
                .where(filter=FieldFilter("gray_swan_version", "==", version))
                .where(filter=FieldFilter("model_name", "==", model_name))
                .limit(limit)
            )
            
            if start_after:
                query = query.start_after(start_after)
                
            docs = await query.get()
            results = []
            
            for doc in docs:
                result_data = doc.to_dict()
                result_data["id"] = doc.id  # Add the document ID to the result
                results.append(result_data)
                
            return results
        except Exception as e:
            logging.error(f"Error getting benchmark results from Firestore by version and model name: {e}")
            raise
            
    @retry()
    async def get_benchmark_results_by_model_category_success(
        self,
        model_name: str,
        category: str,
        success_status: bool,
        limit: int = 50,
        start_after: Optional[dict] = None,
    ) -> List[dict]:
        """
        Retrieves benchmark results from the 'benchmark_results' collection in Firestore by model name, category, and success status.

        Args:
            model_name (str): The model name to filter results by.
            category (str): The category to filter results by.
            success_status (bool): The success status to filter results by.
            limit (int): The maximum number of results to retrieve. Defaults to 50.
            start_after (Optional[dict]): The document data to start the query after, for pagination. Defaults to None.

        Returns:
            List[dict]: A list of benchmark result data dictionaries.
        """
        try:
            query = (
                self.db.collection("benchmark_results")
                .where(filter=FieldFilter("model_name", "==", model_name))
                .where(filter=FieldFilter("category", "==", category))
                .where(filter=FieldFilter("success", "==", success_status))
                .limit(limit)
            )
            
            if start_after:
                query = query.start_after(start_after)
                
            docs = await query.get()
            results = []
            
            for doc in docs:
                result_data = doc.to_dict()
                result_data["id"] = doc.id  # Add the document ID to the result
                results.append(result_data)
                
            return results
        except Exception as e:
            logging.error(f"Error getting benchmark results from Firestore by model name, category, and success status: {e}")
            raise
            
    # Helper functions for prompt generation and management
    
    def _calculate_prompt_hash(self, prompt_text: str) -> str:
        """
        Calculate a hash for a prompt text.
        
        Args:
            prompt_text (str): The prompt text to hash.
            
        Returns:
            str: The SHA-256 hash of the prompt text.
        """
        return hashlib.sha256(prompt_text.encode()).hexdigest()
        
    def _generate_prompt_id(self, prompt_data: Dict[str, Any]) -> str:
        """
        Generate a unique ID for a prompt.
        
        Args:
            prompt_data (Dict[str, Any]): The prompt data.
            
        Returns:
            str: A unique ID for the prompt.
        """
        # Use a combination of category, target, and a hash of the prompt text
        components = []
        
        if "category" in prompt_data:
            components.append(prompt_data["category"])
            
        if "target" in prompt_data:
            components.append(prompt_data["target"])
            
        if "prompt_text" in prompt_data:
            # Add a shortened hash of the prompt text
            prompt_hash = self._calculate_prompt_hash(prompt_data["prompt_text"])
            components.append(prompt_hash[:8])  # Use first 8 characters of the hash
        
        # If we don't have enough components, use a UUID
        if not components:
            return str(uuid.uuid4())
            
        # Join the components with underscores
        return "_".join(components)
