import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

class Logger:
    """Centralized logging utility for the application."""
    
    _instance: Optional[logging.Logger] = None
    
    @classmethod
    def get_logger(cls, name: str = "CompliantByDefault", log_file: Optional[str] = None) -> logging.Logger:
        """
        Get or create a logger instance.
        
        Args:
            name: Logger name
            log_file: Optional file path for logging
            
        Returns:
            Configured logger instance
        """
        if cls._instance is None:
            cls._instance = cls._setup_logger(name, log_file)
        return cls._instance
    
    @staticmethod
    def _setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
        """Configure and return a logger."""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # File handler (if specified)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
        
        return logger

# Global logger instance
logger = Logger.get_logger()
