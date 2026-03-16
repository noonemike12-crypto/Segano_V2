import logging
import os
from datetime import datetime

class SiengLogger:
    _instance = None
    _log_buffer = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SiengLogger, cls).__new__(cls)
            cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self):
        self.logger = logging.getLogger("SIENG_PRO")
        self.logger.setLevel(logging.DEBUG)

        # Create logs directory if not exists
        if not os.path.exists("logs"):
            os.makedirs("logs")

        log_file = f"logs/debug_{datetime.now().strftime('%Y%m%d')}.log"
        
        # File Handler
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s')
        fh.setFormatter(formatter)

        # Console Handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def log(self, level, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {level.upper()}: {message}"
        self._log_buffer.append(log_entry)
        
        if level.lower() == 'info':
            self.logger.info(message)
        elif level.lower() == 'debug':
            self.logger.debug(message)
        elif level.lower() == 'error':
            self.logger.error(message, exc_info=True)
        elif level.lower() == 'warning':
            self.logger.warning(message)

    def get_buffer(self):
        return "\n".join(self._log_buffer)

    def clear_buffer(self):
        self._log_buffer = []

# Global instance
logger = SiengLogger()
