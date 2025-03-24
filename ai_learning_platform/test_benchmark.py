import asyncio
import logging
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_learning_platform.templates.vectorstrategist_template import VectorStrategistTemplate

from .firebase_init import initialize_firebase

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test():
    try:
        initialize_firebase()
        logger.info("Creating VectorStrategistTemplate")
        template = VectorStrategistTemplate('test')
        
        logger.info("Running advanced benchmark")
        result = await template.run_advanced_benchmark(
            category='confidentiality_breach',
            target='system_prompt'
        )
        
        logger.info(f"Benchmark completed with result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting test")
    asyncio.run(test())
    logger.info("Test completed")