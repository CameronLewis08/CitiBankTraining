import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


class Logger:
    def __init__(self, name, log_file="app.log", level=logging.INFO):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)

        if not self._logger.handlers:
            formatter = logging.Formatter(
                "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)

            file_handler = RotatingFileHandler(
                os.path.join(LOG_DIR, log_file),
                maxBytes=1_000_000,
                backupCount=3,
            )
            file_handler.setFormatter(formatter)

            self._logger.addHandler(console_handler)
            self._logger.addHandler(file_handler)

    def info(self, message):
        self._logger.info(message)

    def warning(self, message):
        self._logger.warning(message)

    def error(self, message):
        self._logger.error(message)
