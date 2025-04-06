import logging
import sys
import time
import os

class Logger:
    def __init__(self, log_level=None, log_dir=None, handlers=[]):
        if log_level:
            self.log_level = log_level
        else:
            self.log_level = logging.INFO
        
        # Get the current timestamp
        timestamp = time.strftime("%Y%m%d_%H%M")

        # Create a unique log file name
        log_file_path = os.path.join("logs", f"app_{timestamp}.log")

        if log_dir:
            self.log_dir = log_dir
        else:   
            self.log_dir = log_file_path # '03312025_164000/logs.log'

        if len(handlers) > 0:
            self.handlers = handlers
        else:
            self.handlers = ['STREAM', 'FILE']

        self.formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    def __str__(self):
        return f"{Logger.__name__}"
        
    def get_logger(self):
        """
            Configure logging
        """
        # logging.basicConfig(level=self.log_level, format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger()
        logger.setLevel(self.log_level)
        
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(self.log_level)
        stdout_handler.setFormatter(self.formatter)

        file_handler = logging.FileHandler(self.log_dir)
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(self.formatter)

        for handler in self.handlers:
            if handler == 'FILE':
                logger.addHandler(file_handler)
            if handler ==  'STREAM':
                logger.addHandler(stdout_handler)
        
        return logger