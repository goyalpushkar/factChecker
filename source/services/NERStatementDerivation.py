from source.services.lib.readProperties import PropertiesReader
from source.services.lib.utils import Utils
from source.services.lib.Logger import Logger 
import spacy
import nltk
import re
import en_core_web_sm
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag


# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NERStatementDerivation:
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
        
        if 'utils' in kwargs:
            self.utils = kwargs['utils']
        else:
            self.utils = Utils(kwargs={"logger":self.logger, "properties":self.properties})
        
        self.spc = None  # Initialize to None
        try:
            # https://spacy.io/models
            # en_core_web_sm is a small English pipeline trained on written web text
            #  (blogs, news, comments), that includes vocabulary, syntax and entities.
            self.spc = spacy.load("en_core_web_sm")
            self.logger.info("Spacy model 'en_core_web_sm' loaded successfully.")
        except OSError as e:
            self.logger.error(f"Error loading Spacy model 'en_core_web_sm': {e}")
            self.logger.error("Attempting to download 'en_core_web_sm'...")
            try:
                spacy.cli.download("en_core_web_sm")
                self.spc = spacy.load("en_core_web_sm")
                self.logger.info("Spacy model 'en_core_web_sm' downloaded and loaded successfully.")
            except Exception as download_error:
                self.logger.error(f"Failed to download and load 'en_core_web_sm': {download_error}")


        # Use code with caution, suggested code may be subject to licenses
        # https://github.com/I4-Projektseminar-HHU-2017/i4-projekt-wissenstechnologien-got-mining
        # License unknownPowered by Gemini
        # Download necessary NLTK resources (only need to do this once)
        # try:
        #     nltk.data.find('tokenizers/punkt')
        # except LookupError:
        #     nltk.download('punkt')
        #     nltk.download('punkt_tab')
        #     self.logger.info("NLTK 'punkt' tokenizer downloaded.")
        # except Exception as e:
        #     self.logger.error(f"Error downloading NLTK 'punkt': {e}")

        # try:
        #     nltk.data.find('tokenizers/wordnet')
        # except LookupError:
        #     nltk.download('wordnet')
        #     self.logger.info("NLTK 'wordnet' tokenizer downloaded.")
        # except Exception as e:
        #     self.logger.error(f"Error downloading NLTK 'wordnet': {e}")

        # try:
        #     nltk.data.find('corpora/stopwords')
        # except LookupError:
        #     nltk.download('stopwords')
        #     self.logger.info("NLTK 'stopwords' corpus downloaded.")
        # except Exception as e:
        #     self.logger.error(f"Error downloading NLTK 'stopwords': {e}")

        # try:
        #     nltk.data.find('taggers/averaged_perceptron_tagger')
        # except LookupError:
        #     nltk.download('averaged_perceptron_tagger')
        #     nltk.download('averaged_perceptron_tagger_eng')
        #     self.logger.info("NLTK 'averaged_perceptron_tagger' downloaded.")
        # except Exception as e:
        #     self.logger.error(f"Error downloading NLTK 'averaged_perceptron_tagger': {e}")

    def __str__(self):
        return f"{NERStatementDerivation.__name__}"


    def derive_spacy_statements(self, text):
        """
        Extracts potential factual statements from a given text.
        """
        if self.spc is None:
            self.logger.error("Spacy model not loaded. Cannot derive Spacy statements.")
            return []

        try:
            doc = self.spc(text)
            factual_statements = []
            for sent in doc.sents:
                # Filter statements with named entities (suggests factual info)
                if any(ent.label_ in ["PERSON", "GPE", "ORG", "DATE", "MONEY"] for ent in sent.ents):
                    factual_statements.append(sent.text)
            return factual_statements
        except Exception as e:
            self.logger.error(f"Error in derive_spacy_statements: {e}")
            return []

    def derive_nltk_statements(self, text):
        """
        Extracts potential factual statements from a given text.

        This function uses a combination of sentence tokenization, part-of-speech
        tagging, and filtering to identify statements that are likely to be factual.

        Args:
            text (str): The input text from which to extract statements.

        Returns:
            list: A list of strings, where each string is a potential factual statement.
                Returns an empty list if no statements are found or if the input is invalid.
        """
        if not isinstance(text, str) or not text.strip():
            print("Invalid input: Input must be a non-empty string.")
            return []

        # 1. Sentence Tokenization - It adds \n if sentence starts with a new empty line
        sentences = sent_tokenize(text)
        self.logger.info(f"derive_nltk_statements: Number of sentences: {len(sentences)}\nSentences: {sentences}")

        factual_statements = []
        for sentence in sentences:
            # 2. Basic Filtering (length, presence of verbs)
            if len(sentence.split()) < 3:  # Skip very short sentences
                continue
            if not any(char.isalpha() for char in sentence): # Skip if no alphabets
                continue

            # 2.1. Remove references as it comes in wiki text
            # Removed [1], [2], [3] etc.
            # self.logger.info(f"derive_nltk_statements: Original sentence: {sentence}")
            sentence = re.sub(r"\[\d+\]", "", sentence).replace("\n", "")
            # self.logger.info(f"derive_nltk_statements: Removed References sentence: {sentence}")

            # 3. Part-of-Speech (POS) Tagging
            tagged_words = pos_tag(word_tokenize(sentence))
            # self.logger.info(f"derive_nltk_statements: Tagged words: {tagged_words}")
            # VBP, PRP, IN, RB, DT, VBZ, VB, VBD, VBN, JJ, NN, NNS, CD, JJR, JJS

            # 4. Filtering based on POS tags and content
            is_factual = False
            has_noun = False
            has_verb = False
            has_cardinal = False
            has_symbol = False
            for word, tag in tagged_words:
                if tag.startswith('NN'):  # Noun (singular or plural)
                    has_noun = True
                elif tag.startswith('VB'):  # Verb (base form, past tense, etc.)
                    has_verb = True
                elif tag in ['CD']: # Cardinal numbers
                    is_factual = True
                    has_cardinal = True
                elif tag in ['SYM']:
                    has_symbol = True
                elif tag in ['JJ', 'JJR', 'JJS']: # Adjective
                    is_factual = True

            # self.logger.info(f"derive_nltk_statements: is_factual: {is_factual}, has_noun: {has_noun}, has_verb: {has_verb}")
            if has_noun and has_verb:
                is_factual = True

            # 5. Remove questions and commands
            if sentence.endswith('?') or sentence.endswith('!'):
                is_factual = False
            # self.logger.info(f"derive_nltk_statements: is_factual: {is_factual}")
            
            # 6. Remove stop words
            stop_words = set(stopwords.words('english'))
            # {'have', 'they', 'as', "you've", 's', 'below', 'm', 'once', 'll', 'those', "you'll", 'how', 'couldn', 'ma', "i'm", 'ours', "don't", 'same', "hadn't", 'each', 'or', 'will', 'ourselves', 'an', 'aren', 'yourselves', 'then', 'some', "hasn't", 'now', "she'll", 'into', 'after', 'such', 'them', 'during', 'there', 'herself', "we'd", 'o', 'did', 'their', 'before', "he's", "i'll", 'only', 'shouldn', 'down', 'between', 'his', 'he', "needn't", 't', "it'd", 'don', 'had', "they're", 'why', 'hasn', "won't", 'your', 'it', 'd', 'myself', 'me', "we'll", 'yourself', 'my', 'do', 'our', 'does', 'no', "didn't", "she'd", 'when', 'any', 'what', 'which', 'you', "we've", "aren't", "should've", 'him', 'ain', "haven't", 'with', 'and', 'on', 'doesn', 'am', 'in', 'has', 'be', 'its', "that'll", 'up', "he'll", 're', 'here', 'both', 'isn', 'most', 'for', 'is', 'were', 'this', 'been', 'above', 'not', "we're", 'himself', 'she', 'who', "it'll", "you're", 'the', 'out', 'i', 'than', 'if', 'too', "it's", 'through', 'under', 'wouldn', 'where', 'hadn', 'by', 'themselves', 'about', 'are', 'having', "they'd", 'very', 'other', "wasn't", 'more', 'just', 'all', 'of', 've', "doesn't", 'can', 'should', "they've", "shan't", 'so', "you'd", "couldn't", 'a', 'own', 'while', 'mightn', 'because', 'from', 'that', 'further', "mightn't", 'whom', "she's", 'nor', "they'll", 'theirs', 'her', 'at', 'but', 'haven', 'mustn', 'itself', "wouldn't", 'we', "i've", "weren't", "shouldn't", 'over', 'was', "he'd", 'against', 'shan', 'weren', 'doing', 'won', 'y', 'again', 'these', 'until', 'to', "i'd", 'hers', "isn't", 'yours', 'didn', 'off', 'wasn', 'being', 'needn', "mustn't", 'few'}
            # self.logger.info(f"derive_nltk_statements: stop_words: {stop_words}")
            words = word_tokenize(sentence)
            filtered_words = [w for w in words if not w.lower() in stop_words]
            if len(filtered_words) < 2:
                is_factual = False
            
            # 7. Only take that has numeric value in the sentence
            if has_cardinal or has_symbol:
                is_factual = True
            else:
                is_factual = False

            self.logger.info(f"derive_nltk_statements: is_factual: {is_factual}\n\n")

            if is_factual:
                factual_statements.append(sentence)

        return factual_statements