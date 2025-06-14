import configparser
from source.services.lib.Logger import Logger 

# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PropertiesReader:
    def __init__(self, file_path=None, kwargs=None):
        """
        Initializes the PropertiesReader with the path to the properties file.

        Args:
            file_path (str): The path to the properties file.
        """
        if 'logger' in kwargs:
            self.logger = kwargs['logger']
        else:
            self.loging = Logger()
            self.logger = self.loging.get_logger()

        if file_path is None:
            file_path = "/Users/goyalpushkar/GitHub/factChecker/config.properties"

        self.file_path = file_path
        self.config = configparser.ConfigParser()
        self.load_properties()
        
    def load_properties(self):
        """
        Loads the properties from the file.
        """
        try:
            with open(self.file_path, 'r') as configfile:
                self.config.read_file(configfile)
            self.logger.info(f"load_properties: Successfully loaded properties from {self.file_path}")
        except FileNotFoundError:
            self.logger.error(f"load_properties: Properties file not found: {self.file_path}")
            raise
        except configparser.Error as e:
            self.logger.error(f"load_properties: Error parsing properties file: {e}")
            raise

    def get_property(self, section, key, default=None):
        """
        Retrieves a property value from the specified section and key.

        Args:
            section (str): The section name in the properties file.
            key (str): The key name for the property.
            default (any, optional): The default value to return if the property is not found. Defaults to None.

        Returns:
            str or any: The property value if found, otherwise the default value.
        """
        try:
            if self.config.has_section(section) and self.config.has_option(section, key):
                return self.config.get(section, key)
            else:
                self.logger.warning(f"Property '{key}' not found in section '{section}' in {self.file_path}. Returning default value: {default}")
                return default
        except configparser.Error as e:
            self.logger.error(f"Error getting property: {e}")
            return default

    def get_property_int(self, section, key, default=None):
        """
        Retrieves a property value as an integer from the specified section and key.

        Args:
            section (str): The section name in the properties file.
            key (str): The key name for the property.
            default (int, optional): The default value to return if the property is not found or cannot be converted to an integer. Defaults to None.

        Returns:
            int or any: The property value as an integer if found and convertible, otherwise the default value.
        """
        try:
            if self.config.has_section(section) and self.config.has_option(section, key):
                return self.config.getint(section, key)
            else:
                self.logger.warning(f"Property '{key}' not found in section '{section}' in {self.file_path}. Returning default value: {default}")
                return default
        except ValueError:
            self.logger.error(f"Property '{key}' in section '{section}' is not an integer. Returning default value: {default}")
            return default
        except configparser.Error as e:
            self.logger.error(f"Error getting property: {e}")
            return default

    def get_property_boolean(self, section, key, default=None):
        """
        Retrieves a property value as a boolean from the specified section and key.

        Args:
            section (str): The section name in the properties file.
            key (str): The key name for the property.
            default (bool, optional): The default value to return if the property is not found or cannot be converted to a boolean. Defaults to None.

        Returns:
            bool or any: The property value as a boolean if found and convertible, otherwise the default value.
        """
        try:
            if self.config.has_section(section) and self.config.has_option(section, key):
                return self.config.getboolean(section, key)
            else:
                self.logger.warning(f"Property '{key}' not found in section '{section}' in {self.file_path}. Returning default value: {default}")
                return default
        except ValueError:
            self.logger.error(f"Property '{key}' in section '{section}' is not a boolean. Returning default value: {default}")
            return default
        except configparser.Error as e:
            self.logger.error(f"Error getting property: {e}")
            return default

# Example Usage:
# if __name__ == "__main__":
#     # Create a sample properties file for testing
#     with open("config.properties", "w") as f:
#         f.write("[database]\n")
#         f.write("host = localhost\n")
#         f.write("port = 5432\n")
#         f.write("user = myuser\n")
#         f.write("password = mypassword\n")
#         f.write("enabled = true\n")
#         f.write("\n")
#         f.write("[api]\n")
#         f.write("api_key = your_api_key\n")
#         f.write("timeout = 10\n")
#         f.write("debug = false\n")

#     try:
#         properties = PropertiesReader("config.properties")

#         # Get string properties
#         db_host = properties.get_property("database", "host")
#         db_user = properties.get_property("database", "user")
#         api_key = properties.get_property("api", "api_key")
#         non_existent = properties.get_property("database", "non_existent", "default_value")

#         # Get integer properties
#         db_port = properties.get_property_int("database", "port")
#         api_timeout = properties.get_property_int("api", "timeout")
#         invalid_int = properties.get_property_int("api", "api_key", 0) # will return 0 as default
        
#         # Get boolean properties
#         db_enabled = properties.get_property_boolean("database", "enabled")
#         api_debug = properties.get_property_boolean("api", "debug")
#         invalid_bool = properties.get_property_boolean("api", "timeout", False) # will return false as default

#         print(f"Database Host: {db_host}")
#         print(f"Database User: {db_user}")
#         print(f"Database Port: {db_port}")
#         print(f"Database Enabled: {db_enabled}")
#         print(f"API Key: {api_key}")
#         print(f"API Timeout: {api_timeout}")
#         print(f"API Debug: {api_debug}")
#         print(f"Non-existent property: {non_existent}")
#         print(f"Invalid Integer Property: {invalid_int}")
#         print(f"Invalid Boolean Property: {invalid_bool}")

#     except Exception as e:
#         print(f"An error occurred: {e}")