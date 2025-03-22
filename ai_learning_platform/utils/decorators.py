from functools import wraps
from typing import Any, Callable, Dict, Optional
import logging
import asyncio
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class RetryableError(Exception):
    pass

class ValidationError(Exception):
    pass

@asynccontextmanager
async def timeout(seconds: float):
    try:
        await asyncio.wait_for(asyncio.sleep(seconds), timeout=seconds)
    except asyncio.TimeoutError:
        raise TimeoutError("Operation timed out")

def handle_agent_operation(
    confidence_threshold: float = 0.7,
    fallback_enabled: bool = True
):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs) -> Dict[str, Any]:
            try:
                # Pre-execution validation
                await self._validate_operation_params(func.__name__, args, kwargs)
                
                # Execute with timeout and retry logic
                async with timeout(self.config.timeout):
                    for attempt in range(self.config.max_retries):
                        try:
                            confidence = await self.get_confidence_score(
                                args[0] if args else None
                            )
                            
                            if confidence < confidence_threshold:
                                if not fallback_enabled:
                                    return {
                                        "error": "Confidence below threshold",
                                        "confidence": confidence,
                                        "threshold": confidence_threshold
                                    }
                                return await self._handle_fallback(
                                    func.__name__, *args, **kwargs
                                )
                            
                            result = await func(self, *args, **kwargs)
                            
                            # Post-execution validation
                            if not await self._validate_result(result):
                                raise ValidationError("Invalid result format")
                            
                            return {
                                "result": result,
                                "confidence": confidence,
                                "agent": self.__class__.__name__,
                                "attempts": attempt + 1
                            }
                            
                        except RetryableError as e:
                            if attempt == self.config.max_retries - 1:
                                raise
                            await asyncio.sleep(self._get_backoff_delay(attempt))
                            
            except TimeoutError:
                return self._handle_timeout(func.__name__, args, kwargs)
            except ValidationError as e:
                return self._handle_validation_error(e, func.__name__)
            except Exception as e:
                return self._handle_unexpected_error(e, func.__name__)
        return wrapper
    return decorator
