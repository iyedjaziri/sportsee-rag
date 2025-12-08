import logging
import logfire
from src.core.config import settings

def setup_logging():
    """Configure logging with Logfire and standard logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger("sportsee")
