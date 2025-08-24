import logging
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("/tmp/logs")
logs_dir.mkdir(parents=True, exist_ok=True)


# Configure logging
def setup_logging():
    log_file = logs_dir / f"wenotify_{datetime.now().strftime('%Y-%m-%d')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ],
    )

    # Create logger
    logger = logging.getLogger("wenotify")
    return logger


logger = setup_logging()
