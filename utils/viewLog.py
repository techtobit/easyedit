import logging
from rich.logging import RichHandler

file_handler = logging.FileHandler("easyedit.log")
file_handler.setLevel(logging.INFO)

logging.basicConfig(
		level=logging.INFO,
		format="%(levelname)s - %(message)s",
		# datefmt="%Y-%m-%d %H:%M:%S",
		handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("easyedit_logger")