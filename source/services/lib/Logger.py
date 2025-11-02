import logging
import sys
import time
import os

class Logger:
    def __init__(self, log_level=None, log_dir=None, handlers=[], kwargs=None):
        if log_level:
            self.log_level = log_level
        else:
            self.log_level = logging.INFO
        
        # if 'properties' in kwargs:
        #     self.properties = kwargs['properties']
        # else:
        #     self.properties = PropertiesReader()
        
        # Get the current timestamp
        timestamp = time.strftime("%Y%m%d_%H%M")

        # Create a unique log file name        
        # print(os.getcwd()) # Temp Print Pushkar
        # print(f"log_dir: {log_dir}") # Temp Print Pushkar
        if log_dir:
            curr_log_dir = log_dir
        else:
            # from source.services.lib.readProperties import PropertiesReader
            # self.properties = PropertiesReader() 
            # curr_log_dir = self.properties.get_property("folders", "log_file_path")
            curr_log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            if not curr_log_dir:
                curr_log_dir = os.path.join(os.getcwd(), 'logs')

        # print(f"curr_log_dir: {curr_log_dir}") # Temp Print Pushkar
        self.log_dir = os.path.join(curr_log_dir, f"app_{timestamp}.log")
        print(f"self.log_dir: {self.log_dir}") # Temp Print Pushkar

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