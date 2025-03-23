# ai_learning_platform/utils/benchmarking.py

import time
import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path

from ..models.enhanced_model_manager import EnhancedModelManager, ModelProvider

logger = logging.getLogger(__name__)

class Benchmarker:
    """
    Benchmarks model performance and reliability.
    
    This class provides tools for benchmarking different models and providers,
    measuring performance, reliability, and comparing fallback scenarios.
    """
    
    def __init__(
        self,
        model_manager: Optional[EnhancedModelManager] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Benchmarker.
        
        Args:
            model_manager: Optional EnhancedModelManager instance
            config: Optional configuration dictionary
        """
        self.model_manager = model_manager or EnhancedModelManager()
        self.config = config or {}
        
        # Default benchmark settings
        self.benchmark_dir = Path(self.config.get('benchmark_dir', 'benchmarks'))
        self.benchmark_dir.mkdir(parents=True, exist_ok=True)
        
        # Standard test cases
        self.test_cases = self.config.get('test_cases', [
            "What is machine learning?",
            "Explain the concept of recursion in programming.",
            "How does a neural network work?",
            "What are the key principles of cybersecurity?",
            "Compare and contrast different machine learning algorithms."
        ])
    
    async def benchmark_provider(
        self,
        provider: str,
        model_name: str,
        test_cases: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Benchmark a specific provider and model.
        
        Args:
            provider: The provider to benchmark
            model_name: The model name to benchmark
            test_cases: Optional list of test cases
            **kwargs: Additional arguments to pass to the model
            
        Returns:
            Dictionary with benchmark results
        """
        test_cases = test_cases or self.test_cases
        results = []
        total_tokens = 0
        
        for i, test_case in enumerate(test_cases):
            logger.info(f"Running test case {i+1}/{len(test_cases)} for {provider}/{model_name}")
            
            try:
                start_time = time.time()
                response = await self.model_manager.generate_response(
                    prompt=test_case,
                    provider=provider,
                    model_name=model_name,
                    **kwargs
                )
                end_time = time.time()
                response_time = end_time - start_time
                
                # Extract token usage
                token_usage = response.get('token_usage', {})
                total_tokens += token_usage.get('total_tokens', 0)
                
                results.append({
                    'test_case': test_case,
                    'response_time': response_time,
                    'success': True,
                    'content_length': len(response.get('content', '')),
                    'token_usage': token_usage,
                    'error': None
                })
                
            except Exception as e:
                logger.error(f"Error in benchmark for {provider}/{model_name}: {str(e)}")
                results.append({
                    'test_case': test_case,
                    'response_time': None,
                    'success': False,
                    'content_length': 0,
                    'token_usage': {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0},
                    'error': str(e)
                })
                
            # Add a small delay between tests
            await asyncio.sleep(1)
        
        # Calculate aggregate metrics
        successful_results = [r for r in results if r['success']]
        avg_response_time = (
            sum(r['response_time'] for r in successful_results) / len(successful_results)
            if successful_results else None
        )
        success_rate = len(successful_results) / len(results) if results else 0
        
        benchmark_result = {
            'provider': provider,
            'model': model_name,
            'avg_response_time': avg_response_time,
            'success_rate': success_rate,
            'total_tokens': total_tokens,
            'results': results,
            'timestamp': time.time()
        }
        
        # Save benchmark results
        self._save_benchmark(benchmark_result)
        
        return benchmark_result
    
    async def benchmark_fallback_scenarios(
        self,
        primary_provider: str,
        primary_model: str,
        fallback_provider: str,
        fallback_model: str,
        error_types: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Benchmark fallback scenarios.
        
        Args:
            primary_provider: The primary provider
            primary_model: The primary model
            fallback_provider: The fallback provider
            fallback_model: The fallback model
            error_types: Types of errors to simulate
            **kwargs: Additional arguments
            
        Returns:
            Dictionary with benchmark results
        """
        error_types = error_types or ['rate_limit', 'token_limit', 'general_error']
        results = []
        
        for error_type in error_types:
            logger.info(f"Testing fallback for {error_type} from {primary_provider}/{primary_model} to {fallback_provider}/{fallback_model}")
            
            # Create test case for this error scenario
            test_prompt = self.test_cases[0]  # Use first test case
            
            try:
                # Set up for simulating the error
                if error_type == 'rate_limit':
                    # Simulate rate limit by maxing out the tracker
                    max_requests = self.model_manager.rate_limit_tracker.get(primary_provider, {}).get('limit', 10)
                    current_time = time.time()
                    self.model_manager.rate_limit_tracker[primary_provider]['requests'] = [current_time] * (max_requests + 1)
                elif error_type == 'token_limit':
                    # Simulate token limit with a very large prompt
                    test_prompt = test_prompt * 100  # Make prompt very large
                
                # Time the fallback process
                start_time = time.time()
                response = await self.model_manager.generate_response(
                    prompt=test_prompt,
                    provider=primary_provider,
                    model_name=primary_model,
                    **kwargs
                )
                end_time = time.time()
                fallback_time = end_time - start_time
                
                # Check if fallback was used
                fallback_used = response.get('fallback_used', False)
                actual_provider = response.get('provider')
                actual_model = response.get('model')
                
                results.append({
                    'error_type': error_type,
                    'fallback_time': fallback_time,
                    'fallback_used': fallback_used,
                    'actual_provider': actual_provider,
                    'actual_model': actual_model,
                    'success': True,
                    'error': None
                })
                
            except Exception as e:
                logger.error(f"Error in fallback benchmark: {str(e)}")
                results.append({
                    'error_type': error_type,
                    'fallback_time': None,
                    'fallback_used': False,
                    'actual_provider': None,
                    'actual_model': None,
                    'success': False,
                    'error': str(e)
                })
                
            # Reset the rate limit tracker
            if error_type == 'rate_limit':
                self.model_manager.rate_limit_tracker[primary_provider]['requests'] = []
                
            # Add a delay between tests
            await asyncio.sleep(2)
        
        # Calculate fallback success rate
        successful_fallbacks = [r for r in results if r['fallback_used'] and r['success']]
        fallback_success_rate = len(successful_fallbacks) / len(results) if results else 0
        
        benchmark_result = {
            'primary_provider': primary_provider,
            'primary_model': primary_model,
            'fallback_provider': fallback_provider,
            'fallback_model': fallback_model,
            'fallback_success_rate': fallback_success_rate,
            'results': results,
            'timestamp': time.time()
        }
        
        # Save benchmark results
        self._save_benchmark(benchmark_result, 'fallback')
        
        return benchmark_result
    
    async def compare_providers(
        self,
        providers_and_models: List[Dict[str, str]],
        test_cases: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Compare multiple providers and models.
        
        Args:
            providers_and_models: List of provider/model dictionaries
            test_cases: Optional list of test cases
            **kwargs: Additional arguments
            
        Returns:
            Dictionary with comparison results
        """
        test_cases = test_cases or self.test_cases
        results = {}
        
        for entry in providers_and_models:
            provider = entry.get('provider')
            model = entry.get('model')
            
            if not provider or not model:
                logger.warning(f"Skipping invalid entry: {entry}")
                continue
                
            logger.info(f"Benchmarking {provider}/{model}")
            
            try:
                result = await self.benchmark_provider(
                    provider=provider,
                    model_name=model,
                    test_cases=test_cases,
                    **kwargs
                )
                
                results[f"{provider}/{model}"] = result
                
            except Exception as e:
                logger.error(f"Error benchmarking {provider}/{model}: {str(e)}")
                results[f"{provider}/{model}"] = {
                    'provider': provider,
                    'model': model,
                    'error': str(e)
                }
                
            # Add a small delay between tests
            await asyncio.sleep(2)
        
        # Compile comparison
        comparison = {
            'providers_and_models': providers_and_models,
            'results': results,
            'timestamp': time.time()
        }
        
        # Save comparison results
        self._save_benchmark(comparison, 'comparison')
        
        return comparison
    
    def _save_benchmark(
        self,
        result: Dict[str, Any],
        prefix: str = 'benchmark'
    ) -> None:
        """
        Save benchmark results to disk.
        
        Args:
            result: The benchmark result
            prefix: Optional filename prefix
        """
        try:
            timestamp = time.strftime('%Y%m%d%H%M%S')
            path = self.benchmark_dir / f"{prefix}_{timestamp}.json"
            
            with open(path, 'w') as f:
                json.dump(result, f, indent=2)
                
            logger.info(f"Saved benchmark results to {path}")
            
        except Exception as e:
            logger.error(f"Failed to save benchmark results: {str(e)}")
    
    def load_benchmark(self, path: str) -> Dict[str, Any]:
        """
        Load benchmark results from disk.
        
        Args:
            path: Path to benchmark file
            
        Returns:
            Dictionary with benchmark results
        """
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load benchmark results from {path}: {str(e)}")
            return {}
    
    def list_benchmarks(self) -> List[Dict[str, Any]]:
        """
        List all available benchmark results.
        
        Returns:
            List of benchmark metadata
        """
        results = []
        
        for path in self.benchmark_dir.glob('*.json'):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    
                results.append({
                    'path': str(path),
                    'timestamp': data.get('timestamp'),
                    'type': path.stem.split('_')[0],
                    'provider': data.get('provider') or data.get('primary_provider'),
                    'model': data.get('model') or data.get('primary_model')
                })
                
            except Exception as e:
                logger.error(f"Failed to load benchmark metadata from {path}: {str(e)}")
        
        return sorted(results, key=lambda x: x.get('timestamp', 0), reverse=True)