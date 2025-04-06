# Import necessary libraries
import requests
from readProperties import PropertiesReader
from Logger import Logger

# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FactDerivation:
    def __init__(self, kwargs=None):
        if 'logger' in kwargs:
            self.logger = kwargs['logger']
        else:
            self.loging = Logger()
            self.logger = self.loging.get_logger()

        if 'properties' in kwargs:
            self.properties = kwargs['properties']
        else:
            self.properties = PropertiesReader(kwargs={"logger":self.logger})
        # self.api_key = self.properties.get_property("api_key")

    def __str__(self):
        return f"{FactDerivation.__name__}"

    # External API fact-checking (placeholder for a real fact-checking API)
    def check_external_api(self, claim):
        '''
            Check the fact from an external fact-checking API.
            https://developers.google.com/fact-check/tools/api/reference/rest/?apix=true
        '''
        api_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        params = {
            'query': claim,
            'key': self.properties.get_property("api", "google_api_key")
            #'key': 'AIzaSyAQCGcukhhghNdAC65bmzCxglhJKc_XXts'
        }
        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()
            claims = data.get("claims", [])
            if claims:
                return claims[0].get("claimReview", [{}])[0].get("textualRating", "Unknown")
        except requests.RequestException as e:
            self.logger.error(f"External API error: {e}")
        return "Unknown"