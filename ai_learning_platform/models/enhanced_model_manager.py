# ai_learning_platform/models/enhanced_model_manager.py

import time
import logging
import json
import os
from typing import Dict, Any, Optional, List, Union, Callable
from enum import Enum
from pathlib import Path

from ..utils.exceptions import (
    ModelError, CredentialError, RateLimitError, 
    TokenLimitError, ModelResponseError
)
from ..utils.config_manager import ConfigManager
from .model_response_formatter import ModelResponseFormatter
from ..utils.metrics import Metrics
from ..utils.content_filter import ContentFilter
from ..utils.response_quality import ResponseQualityChecker

logger = logging.getLogger(__name__)

class ModelProvider(Enum):
    """Enumeration of supported model providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    OPENROUTER = "openrouter"
    CAMEL = "camel"

class EnhancedModelManager:
    """
    Enhanced model management system with multi-provider support.
    
    This class manages interactions with different LLM providers, handles fallbacks,
    caching, error handling, token tracking, and other advanced features.
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize EnhancedModelManager.
        
        Args:
            config_manager: Optional ConfigManager instance
        """
        self.config_manager = config_manager or ConfigManager()
        self.config = self.config_manager.get_config()
        
        # Initialize clients dictionary
        self.clients = {}
        
        # Set up in-memory cache
        self.cache = {}
        self.cache_settings = self.config.get('cache_settings', {
            'enabled': True,
            'max_size': 100,
            'expiration': 3600  # 1 hour
        })
        
        # Set up rate limit tracking
        self.rate_limit_tracker = {
            ModelProvider.ANTHROPIC.value: {
                'requests': [],
                'limit': self.config.get('rate_limits', {}).get('anthropic', {}).get('requests_per_minute', 10)
            },
            ModelProvider.OPENAI.value: {
                'requests': [],
                'limit': self.config.get('rate_limits', {}).get('openai', {}).get('requests_per_minute', 20)
            },
            ModelProvider.GOOGLE.value: {
                'requests': [],
                'limit': self.config.get('rate_limits', {}).get('google', {}).get('requests_per_minute', 60)  # Example limit
            },
            ModelProvider.OPENROUTER.value: {
                'requests': [],
                'limit': self.config.get('rate_limits', {}).get('openrouter', {}).get('requests_per_minute', 30)  # Example limit
            }
        }
        
        # Set up metrics
        self.metrics = Metrics(self.config.get('metrics', {}))
        
        # Set up content filter
        self.content_filter = ContentFilter(self.config.get('content_filter', {}))
        
        # Set up response quality checker
        self.response_quality_checker = ResponseQualityChecker(
            self.config.get('response_quality', {})
        )
        
        # Initialize clients
        self._setup_clients()
    
    def _setup_clients(self):
        """Set up model clients for each provider."""
        try:
            # Get API keys
            api_keys = self.config.get('api_keys', {})
            
            # Set up Anthropic client
            anthropic_api_key = api_keys.get('anthropic')
            if anthropic_api_key:
                try:
                    from anthropic import Anthropic
                    self.clients[ModelProvider.ANTHROPIC] = Anthropic(api_key=anthropic_api_key)
                    logger.info("Initialized Anthropic client")
                except ImportError:
                    logger.warning("anthropic package not installed. Anthropic models won't be available.")
            else:
                logger.warning("Anthropic API key not found. Anthropic models won't be available.")
            
            # Set up OpenAI client
            openai_api_key = api_keys.get('openai')
            if openai_api_key:
                try:
                    from openai import OpenAI
                    self.clients[ModelProvider.OPENAI] = OpenAI(api_key=openai_api_key)
                    logger.info("Initialized OpenAI client")
                except ImportError:
                    logger.warning("openai package not installed. OpenAI models won't be available.")
            else:
                logger.warning("OpenAI API key not found. OpenAI models won't be available.")
        
            # Set up Google Gemini client
            google_api_key = api_keys.get('google')
            if google_api_key:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=google_api_key)
                    self.clients[ModelProvider.GOOGLE] = genai
                    logger.info("Initialized Google Gemini client")
                except ImportError:
                    logger.warning("google-generativeai package not installed. Google models won't be available.")
            else:
                logger.warning("Google API key not found. Google models won't be available.")
            
            # Set up OpenRouter client
            openrouter_api_key = api_keys.get('openrouter')
            if openrouter_api_key:
                try:
                    from openai import OpenAI
                    self.clients[ModelProvider.OPENROUTER] = OpenAI(
                        api_key=openrouter_api_key,
                        base_url="https://openrouter.ai/api/v1"
                    )
                    logger.info("Initialized OpenRouter client")
                except ImportError:
                    logger.warning("openai package not installed. OpenRouter won't be available.")
            else:
                logger.warning("OpenRouter API key not found. OpenRouter won't be available.")
            
            # Set up CAMeL-AI client
            camel_api_key = api_keys.get('camel')
            if camel_api_key:
                try:
                    from camel_ai import CamelAI
                    self.clients[ModelProvider.CAMEL] = CamelAI(api_key=camel_api_key)
                    logger.info("Initialized CAMeL-AI client")
                except ImportError:
                    try:
                        # Fallback to local import if package name is different
                        import camel_ai
                        self.clients[ModelProvider.CAMEL] = camel_ai
                        logger.info("Initialized CAMeL-AI client via local import")
                    except ImportError:
                        logger.warning("camel_ai package not installed. CAMeL-AI models won't be available.")
            else:
                logger.warning("CAMeL-AI API key not found. CAMeL-AI models won't be available.")
                
        except Exception as e:
            logger.error(f"Error setting up model clients: {str(e)}")

    
    async def generate_response(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        dry_run: bool = False,
        use_cache: Optional[bool] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response from the specified model.
        
        Args:
            prompt: The prompt to send to the model
            provider: The model provider
            model_name: The model name
            dry_run: If True, return a mock response without calling the API
            use_cache: If True, use the cache (if available)
            **kwargs: Additional arguments to pass to the model
            
        Returns:
            Dictionary containing the response and metadata
        """
        # Set default provider and model if not specified
        provider = provider or self.config.get('model_parameters', {}).get('provider', ModelProvider.ANTHROPIC.value)
        model_name = model_name or self.config.get('model_parameters', {}).get('model_name', "claude-3-7-sonnet-20250219")
        
        # Check if caching is enabled
        use_cache = self.cache_settings.get('enabled', True) if use_cache is None else use_cache
        
        # Try to get cached response if available
        if use_cache:
            cache_key = self._get_cache_key(provider, model_name, prompt, kwargs)
            cached_response = self.cache.get(cache_key)
            if cached_response and time.time() - cached_response.get('timestamp', 0) < self.cache_settings.get('expiration', 3600):
                logger.info(f"Using cached response for {provider}/{model_name}")
                return cached_response.get('response')
        
        # For dry runs, return a mock response
        if dry_run:
            logger.info(f"Dry run requested for {provider}/{model_name}")
            return {
                'content': f"This is a mock response for {provider}/{model_name}",
                'provider': provider,
                'model': model_name,
                'raw_response': None,
                'token_usage': {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0},
                'error': None,
                'fallback_used': False,
                'dry_run': True
            }
        
        try:
            # Check rate limits before proceeding
            if not self._check_rate_limits(provider):
                raise RateLimitError(f"Rate limit would be exceeded for {provider}")

            # Start benchmark
            start_time = time.time()

            # Get appropriate provider client
            provider_enum = ModelProvider(provider)
            client = self.clients.get(provider_enum)

            if not client:
                raise ModelError(f"Provider {provider} not available")

            # Get model parameters
            model_params = self.config.get('model_parameters', {}).copy()
            model_params.update(kwargs)

            # Generate response based on provider
            if provider_enum == ModelProvider.ANTHROPIC:
                response = await self._generate_anthropic_response(
                    client, model_name, prompt, model_params
                )
            elif provider_enum == ModelProvider.OPENAI:
                response = await self._generate_openai_response(
                    client, model_name, prompt, model_params
                )
            elif provider_enum == ModelProvider.GOOGLE:
                response = await self._generate_gemini_response(
                    client, model_name, prompt, model_params
                )
            elif provider_enum == ModelProvider.OPENROUTER:
                response = await self._generate_openrouter_response(
                    client, model_name, prompt, model_params
                )
            elif provider_enum == ModelProvider.CAMEL:
                response = await self._generate_camel_response(
                    client, model_name, prompt, model_params
                )
            else:
                raise NotImplementedError(f"Provider {provider} not implemented yet")

            # Calculate benchmark metrics
            end_time = time.time()
            response_time = end_time - start_time

            # Format response
            if provider_enum == ModelProvider.ANTHROPIC:
                formatted_response = ModelResponseFormatter._format_anthropic_response(
                    model_name=model_name,
                    raw_response=response,
                    token_usage=response.usage if hasattr(response, 'usage') else None
                )
            elif provider_enum == ModelProvider.OPENAI:
                formatted_response = ModelResponseFormatter._format_openai_response(
                    model_name=model_name,
                    raw_response=response,
                    token_usage=response.usage if hasattr(response, 'usage') else None
                )
            elif provider_enum == ModelProvider.GOOGLE:
                formatted_response = ModelResponseFormatter._format_gemini_response(
                    model_name=model_name,
                    raw_response=response,
                    token_usage=response.get('usage_metadata') if hasattr(response, 'usage_metadata') else None
                )
            elif provider_enum == ModelProvider.OPENROUTER:
                formatted_response = ModelResponseFormatter._format_openrouter_response(
                    model_name=model_name,
                    raw_response=response,
                    token_usage=response.usage if hasattr(response, 'usage') else None
                )
            elif provider_enum == ModelProvider.CAMEL:
                formatted_response = ModelResponseFormatter._format_camel_response(
                    model_name=model_name,
                    raw_response=response,
                    token_usage=response.get('usage') if hasattr(response, 'get') else None
                )
            else:
                formatted_response = ModelResponseFormatter._format_generic_response(
                    model_name=model_name,
                    raw_response=response,
                    token_usage=None
                )

            # Apply content filter
            filtered_content, issues, is_blocked = self.content_filter.filter_content(
                formatted_response.get('content', '')
            )

            if is_blocked:
                logger.warning(f"Content blocked by filter: {issues}")
                formatted_response['content'] = "Content blocked by content filter."
                formatted_response['filter_issues'] = issues
                formatted_response['content_blocked'] = True
            elif issues:
                formatted_response['content'] = filtered_content
                formatted_response['filter_issues'] = issues
                formatted_response['content_filtered'] = True

            # Check response quality
            quality_check = self.response_quality_checker.check_quality(
                formatted_response.get('content', ''),
                prompt
            )

            formatted_response['quality_check'] = quality_check

            # Track metrics
            self.metrics.track_response_time(
                provider=provider,
                model=model_name,
                query_type='generate',
                response_time=response_time
            )

            if 'token_usage' in formatted_response:
                usage = formatted_response['token_usage']
                self.metrics.track_token_usage(
                    provider=provider,
                    model=model_name,
                    query_type='generate',
                    prompt_tokens=usage.get('prompt_tokens', 0),
                    completion_tokens=usage.get('completion_tokens', 0),
                    total_tokens=usage.get('total_tokens', 0)
                )

            # Cache response if caching is enabled
            if use_cache:
                self.cache[cache_key] = {
                    'timestamp': time.time(),
                    'response': formatted_response
                }

                # Prune cache if it exceeds max size
                if len(self.cache) > self.cache_settings.get('max_size', 100):
                    await self._prune_cache()

            # Update rate limit tracking
            self._update_rate_limit_tracker(provider)

            return formatted_response
        
        except RateLimitError as e:
            logger.warning(f"Rate limit hit for {provider}/{model_name}: {str(e)}")
            self.metrics.track_error(provider, model_name, 'generate', "RateLimitError", str(e))
            return await self._try_fallback(prompt, provider, model_name, kwargs)

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            self.metrics.track_error(provider, model_name, 'generate', type(e).__name__, str(e))
            try:
                return await self._try_fallback(prompt, provider, model_name, kwargs)
            except Exception as fallback_error:
                logger.error(f"Fallback failed: {str(fallback_error)}")
                return {
                    'content': None,
                    'provider': provider,
                    'model': model_name,
                    'raw_response': None,
                    'token_usage': {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0},
                    'error': str(e),
                    'fallback_used': False,
                    'fallback_error': str(fallback_error)
                }
    
    async def _generate_anthropic_response(
        self,
        client,
        model_name: str,
        prompt: str,
        params: Dict[str, Any]
    ) -> Any:
        """
        Generate a response using Anthropic Claude.
        
        Args:
            client: The Anthropic client
            model_name: The model name
            prompt: The prompt to send to the model
            params: Additional parameters
            
        Returns:
            Raw response from Anthropic
        """
        try:
            # Extract parameters
            temperature = params.get('temperature', 0.7)
            max_tokens = params.get('max_tokens', 3000)
            
            # Claude API call
            response = client.messages.create(
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response
        
        except Exception as e:
            # Map to appropriate error types
            if "API key" in str(e):
                raise CredentialError(f"Invalid Anthropic API key: {str(e)}")
            elif "rate limit" in str(e).lower():
                raise RateLimitError(f"Anthropic rate limit exceeded: {str(e)}")
            elif "token limit" in str(e).lower() or "too many tokens" in str(e).lower():
                raise TokenLimitError(f"Anthropic token limit exceeded: {str(e)}")
            else:
                raise ModelError(f"Anthropic error: {str(e)}")
    
    async def _generate_openai_response(
        self,
        client,
        model_name: str,
        prompt: str,
        params: Dict[str, Any]
    ) -> Any:
        """
        Generate a response using OpenAI.
        
        Args:
            client: The OpenAI client
            model_name: The model name
            prompt: The prompt to send to the model
            params: Additional parameters
            
        Returns:
            Raw response from OpenAI
        """
        try:
            # Extract parameters
            temperature = params.get('temperature', 0.7)
            max_tokens = params.get('max_tokens', 3000)
            
            # Check if using newer GPT-4 or GPT-3.5 models (API >=1.0)
            if model_name.startswith(('gpt-4', 'gpt-3.5')):
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            else:
                # Legacy completion API (API <1.0)
                response = client.completions.create(
                    model=model_name,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            
            return response
        
        except Exception as e:
            # Map to appropriate error types
            if "API key" in str(e):
                raise CredentialError(f"Invalid OpenAI API key: {str(e)}")
            elif "rate limit" in str(e).lower():
                raise RateLimitError(f"OpenAI rate limit exceeded: {str(e)}")
            elif "token limit" in str(e).lower() or "maximum context length" in str(e).lower():
                raise TokenLimitError(f"OpenAI token limit exceeded: {str(e)}")
            else:
                raise ModelError(f"OpenAI error: {str(e)}")

    async def _generate_gemini_response(
        self,
        client,
        model_name: str,
        prompt: str,
        params: Dict[str, Any]
    ) -> Any:
        """
        Generate a response using Google Gemini.
        
        Args:
            client: The Google Gemini client
            model_name: The model name
            prompt: The prompt to send to the model
            params: Additional parameters
            
        Returns:
            Raw response from Gemini
        """
        try:
            # Extract parameters
            temperature = params.get('temperature', 0.7)
            max_tokens = params.get('max_tokens', 3000)
            
            # Initialize the model
            model = client.GenerativeModel(model_name=model_name)
            
            # Generate response
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                    "top_p": params.get('top_p', 0.95),
                    "top_k": params.get('top_k', 40)
                }
            )
            
            return response
        
        except Exception as e:
            # Map to appropriate error types
            if "API key" in str(e):
                raise CredentialError(f"Invalid Google API key: {str(e)}")
            elif "quota" in str(e).lower() or "rate limit" in str(e).lower():
                raise RateLimitError(f"Google Gemini rate limit exceeded: {str(e)}")
            elif "tokens" in str(e).lower() and "exceed" in str(e).lower():
                raise TokenLimitError(f"Google Gemini token limit exceeded: {str(e)}")
            else:
                raise ModelError(f"Google Gemini error: {str(e)}")

    async def _generate_openrouter_response(
        self,
        client,
        model_name: str,
        prompt: str,
        params: Dict[str, Any]
    ) -> Any:
        """
        Generate a response using OpenRouter.
        
        Args:
            client: The OpenRouter client
            model_name: The model name
            prompt: The prompt to send to the model
            params: Additional parameters
            
        Returns:
            Raw response from OpenRouter
        """
        try:
            # Extract parameters
            temperature = params.get('temperature', 0.7)
            max_tokens = params.get('max_tokens', 3000)
            
            # Construct request headers with attribution
            headers = {
                "HTTP-Referer": "https://ai-learning-platform.example.com",  # Replace with actual domain
                "X-Title": "AI Learning Platform"  # Replace with actual application name
            }
            
            # OpenRouter uses OpenAI-compatible interface
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                extra_headers=headers
            )
            
            return response
        
        except Exception as e:
            # Map to appropriate error types
            if "API key" in str(e) or "authentication" in str(e).lower():
                raise CredentialError(f"Invalid OpenRouter API key: {str(e)}")
            elif "rate limit" in str(e).lower():
                raise RateLimitError(f"OpenRouter rate limit exceeded: {str(e)}")
            elif "context length" in str(e).lower() or "token limit" in str(e).lower():
                raise TokenLimitError(f"OpenRouter token limit exceeded: {str(e)}")
            else:
                raise ModelError(f"OpenRouter error: {str(e)}")
    
    async def _generate_camel_response(
        self,
        client,
        model_name: str,
        prompt: str,
        params: Dict[str, Any]
    ) -> Any:
        """
        Generate a response using CAMeL-AI.
        
        Args:
            client: The CAMeL-AI client
            model_name: The model name
            prompt: The prompt to send to the model
            params: Additional parameters
            
        Returns:
            Raw response from CAMeL-AI
        """
        try:
            # Extract parameters
            temperature = params.get('temperature', 0.7)
            max_tokens = params.get('max_tokens', 3000)
            
            # Generate response using CAMeL-AI
            response = client.generate(
                model=model_name,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=params.get('top_p', 0.95),
                top_k=params.get('top_k', 40)
            )
            
            return response
        
        except Exception as e:
            # Map to appropriate error types
            if "API key" in str(e) or "authentication" in str(e).lower():
                raise CredentialError(f"Invalid CAMeL-AI API key: {str(e)}")
            elif "rate limit" in str(e).lower() or "quota" in str(e).lower():
                raise RateLimitError(f"CAMeL-AI rate limit exceeded: {str(e)}")
            elif "token" in str(e).lower() and ("limit" in str(e).lower() or "exceed" in str(e).lower()):
                raise TokenLimitError(f"CAMeL-AI token limit exceeded: {str(e)}")
            else:
                raise ModelError(f"CAMeL-AI error: {str(e)}")
    
    async def _generate_camel_response(
        self,
        client,
        model_name: str,
        prompt: str,
        params: Dict[str, Any]
    ) -> Any:
        """
        Generate a response using CAMeL-AI.
        
        Args:
            client: The CAMeL-AI client
            model_name: The model name
            prompt: The prompt to send to the model
            params: Additional parameters
            
        Returns:
            Raw response from CAMeL-AI
        """
        try:
            # Extract parameters
            temperature = params.get('temperature', 0.7)
            max_tokens = params.get('max_tokens', 3000)
            
            # Generate response using CAMeL-AI
            response = client.generate(
                model=model_name,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=params.get('top_p', 0.95),
                top_k=params.get('top_k', 40)
            )
            
            return response
        
        except Exception as e:
            # Map to appropriate error types
            if "API key" in str(e) or "authentication" in str(e).lower():
                raise CredentialError(f"Invalid CAMeL-AI API key: {str(e)}")
            elif "rate limit" in str(e).lower() or "quota" in str(e).lower():
                raise RateLimitError(f"CAMeL-AI rate limit exceeded: {str(e)}")
            elif "token" in str(e).lower() and ("limit" in str(e).lower() or "exceed" in str(e).lower()):
                raise TokenLimitError(f"CAMeL-AI token limit exceeded: {str(e)}")
            else:
                raise ModelError(f"OpenRouter error: {str(e)}")

    async def _generate_camel_response(
        self,
        client,
        model_name: str,
        prompt: str,
        params: Dict[str, Any]
    ) -> Any:
        """
        Generate a response using CAMeL-AI.
        
        Args:
            client: The CAMeL-AI client
            model_name: The model name
            prompt: The prompt to send to the model
            params: Additional parameters
            
        Returns:
            Raw response from CAMeL-AI
        """
        try:
            # Extract parameters
            temperature = params.get('temperature', 0.7)
            max_tokens = params.get('max_tokens', 3000)
            
            # Handle role-playing parameters - unique to CAMeL-AI
            role = params.get('role')
            system_message = params.get('system_message')
            assistant_role = params.get('assistant_role')
            user_role = params.get('user_role')
            
            # Determine which API to use based on parameters
            if role or (assistant_role and user_role):
                # Use role-playing API
                if role:
                    # Single role definition
                    response = client.generate_role_playing_response(
                        model=model_name,
                        role=role,
                        user_message=prompt,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                else:
                    # Dual role definition
                    response = client.generate_agent_chat(
                        model=model_name,
                        assistant_role=assistant_role,
                        user_role=user_role,
                        user_message=prompt,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
            else:
                # Use standard completion API
                response = client.generate_completion(
                    model=model_name,
                    prompt=prompt,
                    system_message=system_message,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
            return response
        
        except Exception as e:
            # Map to appropriate error types
            if "API key" in str(e) or "authentication" in str(e).lower():
                raise CredentialError(f"Invalid CAMeL-AI API key: {str(e)}")
            elif "quota" in str(e).lower() or "rate limit" in str(e).lower():
                raise RateLimitError(f"CAMeL-AI rate limit exceeded: {str(e)}")
            elif "context length" in str(e).lower() or "tokens" in str(e).lower():
                raise TokenLimitError(f"CAMeL-AI token limit exceeded: {str(e)}")
            else:
                raise ModelError(f"CAMeL-AI error: {str(e)}")
    
    async def _try_fallback(
        self,
        prompt: str,
        provider: str,
        model_name: str,
        kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Try fallback models if primary model fails.
        
        Args:
            prompt: The prompt to send to the model
            provider: The original provider
            model_name: The original model name
            kwargs: Additional arguments
            
        Returns:
            Response from fallback model
        """
        # Get fallback models
        fallback_models = self.config.get('fallback_models', [])
        
        if not fallback_models:
            raise ModelError(f"No fallback models configured for {provider}/{model_name}")
        
        # Progressive fallback strategy
        fallback_types = [
            self._try_simpler_query_fallback,
            self._try_different_provider_fallback,
            self._try_last_resort_fallback
        ]
        
        # Try each fallback strategy in sequence
        for fallback_strategy in fallback_types:
            try:
                logger.info(f"Trying fallback strategy: {fallback_strategy.__name__}")
                response = await fallback_strategy(prompt, provider, model_name, kwargs)
                
                # Mark as fallback
                response['fallback_used'] = True
                response['original_provider'] = provider
                response['original_model'] = model_name
                response['fallback_strategy'] = fallback_strategy.__name__
                
                return response
            except Exception as e:
                logger.warning(f"Fallback strategy {fallback_strategy.__name__} failed: {str(e)}")
        
        # If all fallbacks fail, raise error
        raise ModelError(f"All fallback strategies failed for {provider}/{model_name}")

    async def _try_simpler_query_fallback(
        self,
        prompt: str,
        provider: str,
        model_name: str,
        kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Try fallback with simplified query on same model.
        
        Args:
            prompt: The original prompt
            provider: The original provider
            model_name: The original model name
            kwargs: Additional arguments
            
        Returns:
            Response from fallback with simplified query
        """
        # Simplify the query
        simplified_prompt = f"""
        I need a brief and simple response to the following query:
        
        {prompt}
        
        Please keep your response concise and straightforward.
        """
        
        # Reduce tokens and complexity
        simplified_kwargs = kwargs.copy()
        simplified_kwargs['max_tokens'] = min(kwargs.get('max_tokens', 3000), 1000)
        simplified_kwargs['temperature'] = min(kwargs.get('temperature', 0.7), 0.5)
        
        # Try with same provider/model but simplified query
        try:
            provider_enum = ModelProvider(provider)
            client = self.clients.get(provider_enum)
            
            if not client:
                raise ModelError(f"Provider {provider} not available")
                
            # Get model parameters
            model_params = self.config.get('model_parameters', {}).copy()
            model_params.update(simplified_kwargs)
            
            # Generate response based on provider
            if provider_enum == ModelProvider.ANTHROPIC:
                response = await self._generate_anthropic_response(
                    client, model_name, simplified_prompt, model_params
                )
            elif provider_enum == ModelProvider.OPENAI:
                response = await self._generate_openai_response(
                    client, model_name, simplified_prompt, model_params
                )
            elif provider_enum == ModelProvider.GOOGLE:
                response = await self._generate_gemini_response(
                    client, model_name, simplified_prompt, model_params
                )
            elif provider_enum == ModelProvider.OPENROUTER:
                response = await self._generate_openrouter_response(
                    client, model_name, simplified_prompt, model_params
                )
            else:
                raise NotImplementedError(f"Provider {provider} not implemented yet")
            
            # Format response
            if provider_enum == ModelProvider.ANTHROPIC:
                formatted_response = ModelResponseFormatter._format_anthropic_response(
                    model_name=model_name,
                    raw_response=response,
                    token_usage=response.usage if hasattr(response, 'usage') else None,
                    fallback_used=True
                )
            elif provider_enum == ModelProvider.OPENAI:
                formatted_response = ModelResponseFormatter._format_openai_response(
                    model_name=model_name,
                    raw_response=response,
                    token_usage=response.usage if hasattr(response, 'usage') else None,
                    fallback_used=True
                )
            elif provider_enum == ModelProvider.GOOGLE:
                formatted_response = ModelResponseFormatter._format_gemini_response(
                    model_name=model_name,
                    raw_response=response,
                    token_usage=None,
                    fallback_used=True
                )
            elif provider_enum == ModelProvider.OPENROUTER:
                formatted_response = ModelResponseFormatter._format_openrouter_response(
                    model_name=model_name,
                    raw_response=response,
                    token_usage=response.usage if hasattr(response, 'usage') else None,
                    fallback_used=True
                )
            else:
                formatted_response = ModelResponseFormatter._format_generic_response(
                    model_name=model_name,
                    raw_response=response,
                    token_usage=None,
                    fallback_used=True
                )
                
            return formatted_response
        except Exception as e:
            logger.warning(f"Simpler query fallback failed: {str(e)}")
            raise e

    async def _try_different_provider_fallback(
        self,
        prompt: str,
        provider: str,
        model_name: str,
        kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Try fallback with a different provider/model.
        
        Args:
            prompt: The original prompt
            provider: The original provider
            model_name: The original model name
            kwargs: Additional arguments
            
        Returns:
            Response from fallback with different provider
        """
        # Get fallback models
        fallback_models = self.config.get('fallback_models', [])
        
        # Try each fallback model
        for fallback in fallback_models:
            fallback_provider = fallback.get('provider')
            fallback_model = fallback.get('model_name')
            
            # Skip if same as original
            if fallback_provider == provider and fallback_model == model_name:
                continue
                
            logger.info(f"Trying fallback {fallback_provider}/{fallback_model}")
            
            try:
                # Get or initialize provider client
                provider_enum = ModelProvider(fallback_provider)
                client = self.clients.get(provider_enum)
                
                if not client:
                    # Try to initialize if not already done
                    self._setup_clients()
                    client = self.clients.get(provider_enum)
                    
                    if not client:
                        logger.warning(f"Provider {fallback_provider} not available")
                        continue
                
                # Get model parameters
                fallback_kwargs = kwargs.copy()
                if 'model_params' in fallback:
                    fallback_kwargs.update(fallback.get('model_params', {}))
                    
                model_params = self.config.get('model_parameters', {}).copy()
                model_params.update(fallback_kwargs)
                
                # Generate response based on provider
                if provider_enum == ModelProvider.ANTHROPIC:
                    response = await self._generate_anthropic_response(
                        client, fallback_model, prompt, model_params
                    )
                    formatted_response = ModelResponseFormatter._format_anthropic_response(
                        model_name=fallback_model,
                        raw_response=response,
                        token_usage=response.usage if hasattr(response, 'usage') else None,
                        fallback_used=True
                    )
                elif provider_enum == ModelProvider.OPENAI:
                    response = await self._generate_openai_response(
                        client, fallback_model, prompt, model_params
                    )
                    formatted_response = ModelResponseFormatter._format_openai_response(
                        model_name=fallback_model,
                        raw_response=response,
                        token_usage=response.usage if hasattr(response, 'usage') else None,
                        fallback_used=True
                    )
                elif provider_enum == ModelProvider.GOOGLE:
                    response = await self._generate_gemini_response(
                        client, fallback_model, prompt, model_params
                    )
                    formatted_response = ModelResponseFormatter._format_gemini_response(
                        model_name=fallback_model,
                        raw_response=response,
                        token_usage=None,
                        fallback_used=True
                    )
                elif provider_enum == ModelProvider.OPENROUTER:
                    response = await self._generate_openrouter_response(
                        client, fallback_model, prompt, model_params
                    )
                    formatted_response = ModelResponseFormatter._format_openrouter_response(
                        model_name=fallback_model,
                        raw_response=response,
                        token_usage=response.usage if hasattr(response, 'usage') else None,
                        fallback_used=True
                    )
                elif provider_enum == ModelProvider.CAMEL:
                    response = await self._generate_camel_response(
                        client, fallback_model, prompt, model_params
                    )
                    formatted_response = ModelResponseFormatter._format_camel_response(
                        model_name=fallback_model,
                        raw_response=response,
                        token_usage=response.get('usage') if hasattr(response, 'get') else None,
                        fallback_used=True
                    )
                else:
                    raise NotImplementedError(f"Provider {fallback_provider} not implemented yet")
                    
                return formatted_response
                    
            except Exception as e:
                logger.warning(f"Fallback {fallback_provider}/{fallback_model} failed: {str(e)}")
        
        # If all fallbacks fail, raise error
        raise ModelError(f"All fallback models failed for {provider}/{model_name}")

    async def _try_last_resort_fallback(
        self,
        prompt: str,
        provider: str,
        model_name: str,
        kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Last resort fallback with minimal capability.
        
        Args:
            prompt: The original prompt
            provider: The original provider
            model_name: The original model name
            kwargs: Additional arguments
            
        Returns:
            Minimal response as last resort
        """
        # This method provides a very basic generated response as a last resort
        # when all other fallbacks have failed
        
        logger.warning(f"Using last resort fallback for {provider}/{model_name}")
        
        # Extract query type and key terms
        query_terms = prompt.split()[:10]  # First 10 words
        query_type = "informational"
        
        if "?" in prompt:
            query_type = "question"
        elif any(cmd in prompt.lower() for cmd in ["list", "summarize", "explain", "describe"]):
            query_type = "instruction"
        
        # Generate a simple response
        if query_type == "question":
            content = (
                "I'm unable to provide a complete answer at the moment due to technical limitations. "
                "Once those are resolved, I'll be able to help more fully with your question."
            )
        elif query_type == "instruction":
            content = (
                "I'm unable to complete this task at the moment due to technical limitations. "
                "Once those are resolved, I'll be able to follow your instructions more effectively."
            )
        else:
            content = (
                "I'm unable to process your request fully at the moment due to technical limitations. "
                "Once those are resolved, I'll be able to help more effectively."
            )
        
        return {
            'content': content,
            'provider': provider,
            'model': model_name,
            'raw_response': None,
            'token_usage': {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0},
            'error': None,
            'fallback_used': True,
            'original_provider': provider,
            'original_model': model_name,
            'fallback_strategy': '_try_last_resort_fallback'
        }
    
    def _get_cache_key(
        self,
        provider: str,
        model_name: str,
        prompt: str,
        params: Dict[str, Any]
    ) -> str:
        """
        Generate a cache key for the request.
        
        Args:
            provider: The model provider
            model_name: The model name
            prompt: The prompt
            params: Additional parameters
            
        Returns:
            A string key for caching
        """
        # Create a unique key based on provider, model, and prompt
        key_parts = [
            provider,
            model_name,
            prompt[:100],  # Use first 100 chars of prompt to keep key size reasonable
            str(hash(frozenset(sorted(params.items()))))  # Hash of params
        ]
        return ":".join(key_parts)
