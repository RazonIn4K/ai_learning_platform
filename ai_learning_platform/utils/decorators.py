from functools import wraps
from typing import Any, Callable, Dict, Optional
import logging

logger = logging.getLogger(__name__)

def handle_agent_operation(
    confidence_threshold: float = 0.7,
    fallback_enabled: bool = True
):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Dict[str, Any]:
            try:
                confidence = self.get_confidence_score(args[0] if args else None)
                if confidence < confidence_threshold:
                    if not fallback_enabled:
                        return {"error": "Confidence below threshold", "confidence": confidence}
                    return self._handle_fallback(func.__name__, *args, **kwargs)
                    
                result = func(self, *args, **kwargs)
                return {
                    "result": result,
                    "confidence": confidence,
                    "agent": self.__class__.__name__
                }
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                return {"error": str(e)}
        return wrapper
    return decorator
