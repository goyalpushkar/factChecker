# Import necessary libraries
import logging
from readProperties import PropertiesReader
from DB import Database
from NERStatementDerivation import NERStatementDerivation

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class StatementDerivation:
    """
    A class to derive potential factual statements from a given text.   
    """

    def __init__(self, kwargs=None):
        if 'properties' in kwargs:
            self.properties = kwargs['properties']
        else:
            self.properties = PropertiesReader()
        self.db = Database()
        self.statement_derivation = NERStatementDerivation(kwargs={"properties":self.properties})

    def __str__(self):
        return f"{StatementDerivation.__name__}"
    
    def get_factual_statements(self, text, source="all"):
        """
        Extracts potential factual statements from a given text."
        """
        spacy_statements = None
        nltk_statements = None
        factual_statements = None

        logging.info(f"get_factual_statements: Getting factual statements from {text} using {source}")
        if source == "spacy":
            spacy_statements = self.statement_derivation.derive_spacy_statements(text)
        elif source == "nltk":
            nltk_statements = self.statement_derivation.derive_nltk_statements(text)
        else:
            try:
                spacy_statements = self.statement_derivation.derive_spacy_statements(text)
            except Exception as e:
                logging.error(f"Error in Spacy: {e}")
            
            # for testing
            # if not spacy_statements:
            try:
                nltk_statements = self.statement_derivation.derive_nltk_statements(text)
            except Exception as e:
                logging.error(f"Error in NLTK: {e}")

            logging.info(f"get_factual_statements: Spacy Statements: {spacy_statements} \nNLTK Statements: {nltk_statements}")
            # if spacy_statements:
            #     factual_statements = spacy_statements
            # elif nltk_statements:
            #     factual_statements = nltk_statements

        # return factual_statements
        return {"spacy": spacy_statements, "nltk": nltk_statements}