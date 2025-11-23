import json
import os
import re
from typing import Optional, Dict, Any

# Add the project root to sys.path for consistent imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
import sys
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from source.services.lib import readProperties as PropertiesReader
from source.services.lib import Logger

class Utils:
    """
    Handles the generation of SQL queries from natural language using an LLM.
    """

    # def __init__(self, connection_pool: oracledb.SessionPool):
    def __init__(self):
        """
        Initializes the generator with a database connection pool and LLM client.

        Args:
            connection_pool: An oracledb.SessionPool for database schema fetching.
        """
        self.property_reader = PropertiesReader.PropertiesReader()
        self.logger = Logger.Logger.get_logger()

    def read_json(self, lv_text: str) -> Optional[Dict[str, Any]]:
        """
        Reads a JSON string and returns a dictionary.

        Args:
            lv_text: A string in JSON format.   
        Returns:
            A dictionary parsed from the JSON string, or None if parsing fails.
        """
        try:
            # Clean the text to make it valid JSON
            # 1. Find the JSON object within the text
            match = re.search(r'\{.*\}', lv_text, re.DOTALL)
            if not match:
                self.logger.error(f"❌ No JSON object found in the text.")
                return lv_text
            
            json_str = match.group(0)

            # 2. Load the potentially malformed JSON.
            # The `strict=False` argument allows control characters like newlines inside strings.
            return json.loads(json_str, strict=False)

        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Error parsing JSON: {e}")
            return lv_text
        except Exception as e:
            self.logger.error(f"❌ An unexpected error occurred during JSON parsing: {e}")
            return lv_text
