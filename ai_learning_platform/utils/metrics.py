# ai_learning_platform/utils/metrics.py

import time
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class Metrics:
    """
    Collects and reports metrics for the AI Learning Platform.
    
    This class tracks response times, token usage, error rates, and other
    performance metrics to help monitor and optimize platform performance.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Metrics with optional configuration.
        
        Args:
            config: Optional configuration dictionary with metrics settings
        """
        self.config = config or {}
        
        # Storage for metrics
        self._response_times: List[Dict[str, Any]] = []
        self._token_usage: List[Dict[str, Any]] = []
        self._errors: List[Dict[str, Any]] = []
        
        # Thresholds for alerting
        self._response_time_threshold = self.config.get('response_time_threshold', 5.0)  # seconds
        self._error_rate_threshold = self.config.get('error_rate_threshold', 0.1)  # 10%
        
        # Metrics storage path
        self._storage_path = Path(self.config.get('storage_path', 'metrics'))
        self._storage_path.mkdir(parents=True, exist_ok=True)
        
        # Enable logging
        self._log_metrics = self.config.get('log_metrics', True)
    
    def track_response_time(
        self,
        provider: str,
        model: str,
        query_type: str,
        response_time: float
    ) -> None:
        """
        Track model response time.
        
        Args:
            provider: The model provider (e.g., 'anthropic', 'openai')
            model: The model name
            query_type: The type of query (e.g., 'learning_path', 'knowledge')
            response_time: The response time in seconds
        """
        metric = {
            'timestamp': datetime.now().isoformat(),
            'provider': provider,
            'model': model,
            'query_type': query_type,
            'response_time': response_time
        }
        
        self._response_times.append(metric)
        
        # Log if enabled and threshold exceeded
        if self._log_metrics and response_time > self._response_time_threshold:
            logger.warning(
                f"High response time ({response_time:.2f}s) for {provider}/{model} "
                f"on {query_type} query"
            )
        
        # Periodically save metrics
        if len(self._response_times) % 100 == 0:
            self._save_metrics()
    
    def track_token_usage(
        self,
        provider: str,
        model: str,
        query_type: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int
    ) -> None:
        """
        Track token usage.
        
        Args:
            provider: The model provider
            model: The model name
            query_type: The type of query
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            total_tokens: Total tokens used
        """
        metric = {
            'timestamp': datetime.now().isoformat(),
            'provider': provider,
            'model': model,
            'query_type': query_type,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens
        }
        
        self._token_usage.append(metric)
        
        # Periodically save metrics
        if len(self._token_usage) % 100 == 0:
            self._save_metrics()
    
    def track_error(
        self,
        provider: str,
        model: str,
        query_type: str,
        error_type: str,
        error_message: str
    ) -> None:
        """
        Track an error.
        
        Args:
            provider: The model provider
            model: The model name
            query_type: The type of query
            error_type: The type of error
            error_message: The error message
        """
        metric = {
            'timestamp': datetime.now().isoformat(),
            'provider': provider,
            'model': model,
            'query_type': query_type,
            'error_type': error_type,
            'error_message': error_message
        }
        
        self._errors.append(metric)
        
        # Log if enabled
        if self._log_metrics:
            logger.error(
                f"Error in {provider}/{model} on {query_type} query: "
                f"{error_type} - {error_message}"
            )
        
        # Check error rate and alert if necessary
        self._check_error_rate(provider, model)
        
        # Periodically save metrics
        if len(self._errors) % 10 == 0:
            self._save_metrics()
    
    def _check_error_rate(self, provider: str, model: str) -> None:
        """
        Check the error rate for a provider/model and alert if necessary.
        
        Args:
            provider: The model provider
            model: The model name
        """
        # Count recent errors (last 100)
        recent_errors = sum(
            1 for e in self._errors[-100:]
            if e['provider'] == provider and e['model'] == model
        )
        
        if recent_errors >= 100 * self._error_rate_threshold:
            logger.warning(
                f"High error rate detected for {provider}/{model}: "
                f"{recent_errors} errors in the last 100 requests"
            )
    
    def get_average_response_time(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        query_type: Optional[str] = None,
        period: Optional[int] = None
    ) -> float:
        """
        Get average response time, optionally filtered.
        
        Args:
            provider: Optional provider filter
            model: Optional model filter
            query_type: Optional query type filter
            period: Optional period in seconds to consider (e.g., last hour)
            
        Returns:
            Average response time in seconds
        """
        # Filter metrics based on provided filters
        metrics = self._response_times
        
        if provider:
            metrics = [m for m in metrics if m['provider'] == provider]
        if model:
            metrics = [m for m in metrics if m['model'] == model]
        if query_type:
            metrics = [m for m in metrics if m['query_type'] == query_type]
        if period:
            cutoff = (datetime.now() - datetime.timedelta(seconds=period)).isoformat()
            metrics = [m for m in metrics if m['timestamp'] >= cutoff]
        
        if not metrics:
            return 0.0
            
        return sum(m['response_time'] for m in metrics) / len(metrics)
    
    def get_total_token_usage(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        period: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Get total token usage, optionally filtered.
        
        Args:
            provider: Optional provider filter
            model: Optional model filter
            period: Optional period in seconds to consider
            
        Returns:
            Dictionary with token usage statistics
        """
        # Filter metrics based on provided filters
        metrics = self._token_usage
        
        if provider:
            metrics = [m for m in metrics if m['provider'] == provider]
        if model:
            metrics = [m for m in metrics if m['model'] == model]
        if period:
            cutoff = (datetime.now() - datetime.timedelta(seconds=period)).isoformat()
            metrics = [m for m in metrics if m['timestamp'] >= cutoff]
        
        return {
            'prompt_tokens': sum(m['prompt_tokens'] for m in metrics),
            'completion_tokens': sum(m['completion_tokens'] for m in metrics),
            'total_tokens': sum(m['total_tokens'] for m in metrics)
        }
    
    def get_error_rate(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        period: Optional[int] = None
    ) -> float:
        """
        Get error rate, optionally filtered.
        
        Args:
            provider: Optional provider filter
            model: Optional model filter
            period: Optional period in seconds to consider
            
        Returns:
            Error rate as a float between 0 and 1
        """
        # Count total requests
        total_requests = len(self._response_times)
        if total_requests == 0:
            return 0.0
            
        # Count errors
        errors = self._errors
        
        if provider:
            errors = [e for e in errors if e['provider'] == provider]
        if model:
            errors = [e for e in errors if e['model'] == model]
        if period:
            cutoff = (datetime.now() - datetime.timedelta(seconds=period)).isoformat()
            errors = [e for e in errors if e['timestamp'] >= cutoff]
            
            # Also filter total requests for the same period
            requests = [r for r in self._response_times if r['timestamp'] >= cutoff]
            total_requests = len(requests)
            
            if total_requests == 0:
                return 0.0
        
        return len(errors) / total_requests
    
    def _save_metrics(self) -> None:
        """Save metrics to disk."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            
            # Save response times
            if self._response_times:
                path = self._storage_path / f"response_times_{timestamp}.json"
                with open(path, 'w') as f:
                    json.dump(self._response_times, f, indent=2)
                    
            # Save token usage
            if self._token_usage:
                path = self._storage_path / f"token_usage_{timestamp}.json"
                with open(path, 'w') as f:
                    json.dump(self._token_usage, f, indent=2)
                    
            # Save errors
            if self._errors:
                path = self._storage_path / f"errors_{timestamp}.json"
                with open(path, 'w') as f:
                    json.dump(self._errors, f, indent=2)
                    
            logger.info(f"Saved metrics to {self._storage_path}")
            
        except Exception as e:
            logger.error(f"Failed to save metrics: {str(e)}")
    
    def benchmark(
        self,
        provider: str,
        model: str,
        request_func
    ) -> Dict[str, Any]:
        """
        Benchmark model performance.
        
        Args:
            provider: The model provider
            model: The model name
            request_func: Function to make a request to the model
            
        Returns:
            Dictionary with benchmark results
        """
        # Standard test cases for benchmarking
        test_cases = [
            "What is machine learning?",
            "Explain the concept of recursion in programming",
            "How does a neural network work?",
            "What are the key principles of cybersecurity?"
        ]
        
        results = []
        
        for test_case in test_cases:
            start_time = time.time()
            try:
                response = request_func(test_case)
                success = True
                error = None
            except Exception as e:
                response = None
                success = False
                error = str(e)
                
            end_time = time.time()
            response_time = end_time - start_time
            
            results.append({
                'test_case': test_case,
                'response_time': response_time,
                'success': success,
                'error': error
            })
            
        # Calculate aggregate metrics
        avg_response_time = sum(r['response_time'] for r in results) / len(results)
        success_rate = sum(1 for r in results if r['success']) / len(results)
        
        return {
            'provider': provider,
            'model': model,
            'avg_response_time': avg_response_time,
            'success_rate': success_rate,
            'results': results
        }