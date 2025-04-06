# Import necessary libraries
from readProperties import PropertiesReader
from DB import Database
from NERStatementDerivation import NERStatementDerivation
from Logger import Logger

# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class StatementDerivation:
    """
    A class to derive potential factual statements from a given text.   
    """

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
        self.db = Database(kwargs={"logger":self.logger})
        self.statement_derivation = NERStatementDerivation(kwargs={"properties":self.properties, "logger":self.logger})

    def __str__(self):
        return f"{StatementDerivation.__name__}"
    
    def get_factual_statements(self, text, source="all"):
        """
        Extracts potential factual statements from a given text."
        """
        spacy_statements = None
        nltk_statements = None
        factual_statements = None

        self.logger.info(f"get_factual_statements: Getting factual statements from {text} using {source}")
        if source == "spacy":
            spacy_statements = self.statement_derivation.derive_spacy_statements(text)
        elif source == "nltk":
            nltk_statements = self.statement_derivation.derive_nltk_statements(text)
        else:
            try:
                spacy_statements = self.statement_derivation.derive_spacy_statements(text)
            except Exception as e:
                self.logger.error(f"Error in Spacy: {e}")
            
            # for testing
            # if not spacy_statements:
            try:
                nltk_statements = self.statement_derivation.derive_nltk_statements(text)
            except Exception as e:
                self.logger.error(f"Error in NLTK: {e}")

            self.logger.info(f"get_factual_statements: Spacy Statements: {spacy_statements} \nNLTK Statements: {nltk_statements}")
            # if spacy_statements:
            #     factual_statements = spacy_statements
            # elif nltk_statements:
            #     factual_statements = nltk_statements

        # return factual_statements
        return {"spacy": spacy_statements, "nltk": nltk_statements}