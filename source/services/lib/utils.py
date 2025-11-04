from source.services.lib.readProperties import PropertiesReader
from source.services.lib.Logger import Logger
import multiprocessing
import os
import hashlib
# from transformers import utils.ExplicitEnum
import torch
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag

class ReturnTensorTypes(): # ExplicitEnum
    """
    Possible values for the `return_tensors` argument in [`PreTrainedTokenizerBase.__call__`]. Useful for
    tab-completion in an IDE.
    """
    PYTORCH = "pt"
    TENSORFLOW = "tf"
    NUMPY = "np"
    JAX = "jax"
    MLX = "mlx"

class AvailableLanguages():
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    DANISH = "da"
    HINDI = "hi"

class AvailableCountryCodes():
    US = "US"
    ENGLAND = "GB"
    SCOTLAND = "scotland"
    SOUTHAFRICA = "ZA"
    MEXICO = "MX"
    SPAIN = "ES"
    FRANCE = "FR"
    ITALY = "it"
    PORTUGAL = "pt"
    DENMARK = "dk"
    INDIA = "in"

class SummarizationTypes(): 
    """
    Possible values for the summarization types 
    """
    # Summarization types
    EXTRACTIVE_SUMMARY = "extractive"
    ABSTRACTIVE_SUMMARY = "abstractive"

class TokenizationType(): 
    """
    Possible values for the summarization types 
    """
    # Summarization types
    EXTRACTIVE_TOKENIZATION = "extractive"
    ABSTRACTIVE_TOKENIZATION = "abstractive"

class AvailableModels(): 
    """
    Possible values for the available models 
    """
    # Available models
    T5_BASE = "t5-base"
    GOOGLE_PEGASUS = "google/pegasus-xsum"
    FACEBOOK_LARGECNN = "facebook/bart-large-cnn"
    PEGASUS_PARAPHRASE = "tuner007/pegasus_paraphrase"
    MICROSOFT_SPEECH = "microsoft/speecht5_tts"
    MICROSOFT_VOCODER = "microsoft/speecht5_hifigan"

    # model.generate() method parameters - 
    # num_return_sequences  -> the possibility of generating multiple paraphrased sentences
    # num_beams -> the number of beams for beam search. Setting it to 5 will allow the model
    #  to look ahead for five possible words to keep the most likely hypothesis at each time step and choose the one that has the overall highest probability.

class SourceTypes():
    """
    Possible values for the caption sources 
    """
    # source_types
    YOUTUBE = "youtube"
    VIDEO = "video"
    AUDIO = "audio"
    PODCAST = "podcast"
    WIKI = "wiki"

class CaptionSources():
    """
    Possible values for the caption types 
    """
    # caption sources
    NLP = "nlp"
    THIRD_PARTY = "thirdparty"
    GOOGLE = "google"
    DOWNLOAD = "downloadFile"
    ALL = "all"

class TextToAudioSources():
    """
    Possible values for the audio from text sources 
    """
    # audio text sources
    GTTS = "gtts"
    PYTTSX3 = "pyttsx3"
    OPENAI = "openai"
    TRANSFORMERS = "transformers"
    ALL = "all"

class SpeechSynthesizers():
    SAPI5 = "sapi5"     # - SAPI5 on Windows
    NSSS = "nsss"       # - NSSpeechSynthesizer on Mac OS X
    ESPEAK = "espeak"   # - eSpeak on every other platform

class ParallelizationTypes():
    """
    Possible values for the parallelization types 
    """
    # Parallelization types
    MULTI_PROCESSING = "multiprocessing"
    MULTI_THREADING = "multithreading"
    ASYNC = "async"
    SINGLE = "single"

class ParallelizationNumbers():
    """
    Possible values for the parallelization methods 
    """ 
    # Parallelization methods
    CPU_COUNT = multiprocessing.cpu_count()
    # GPU_COUNT = "gpu_count"
    ONE = 1
    FOUR = 4
    EIGHT = 8
    SIXTEEN = 16
    THIRTY_TWO = 32
    HUNDRED_TWENTY_EIGHT = 128
    TWO_HUNDRED_SIXTY_FOUR = 264

class summarySelectedSize():
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    MARGIN = "margin"

    # Mapping of summary selected size to number of sentences
    SUMMARY_SIZE_MAPPING = {
        SMALL: 800,
        MEDIUM: 1300,
        LARGE: 1800,
        MARGIN: 500
    }
    # Mapping of summary selected size to number of sentences    

class Utils:
    def __init__(self, kwargs):
        if 'logger' in kwargs:
            self.logger = kwargs['logger']
        else:
            self.loging = Logger()
            self.logger = self.loging.get_logger()

        if 'properties' in kwargs:
            self.properties = kwargs['properties']
        else:
            self.properties = PropertiesReader(kwargs={"logger":self.logger})
        
        # Use code with caution, suggested code may be subject to licenses
        # https://github.com/I4-Projektseminar-HHU-2017/i4-projekt-wissenstechnologien-got-mining
        # License unknownPowered by Gemini
        # Download necessary NLTK resources (only need to do this once)
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            nltk.download('punkt_tab')
            self.logger.info("NLTK 'punkt' tokenizer downloaded.")
        except Exception as e:
            self.logger.error(f"Error downloading NLTK 'punkt': {e}")

        try:
            nltk.data.find('tokenizers/wordnet')
        except LookupError:
            nltk.download('wordnet')
            self.logger.info("NLTK 'wordnet' tokenizer downloaded.")
        except Exception as e:
            self.logger.error(f"Error downloading NLTK 'wordnet': {e}")

        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
            self.logger.info("NLTK 'stopwords' corpus downloaded.")
        except Exception as e:
            self.logger.error(f"Error downloading NLTK 'stopwords': {e}")

        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger')
            nltk.download('averaged_perceptron_tagger_eng')
            self.logger.info("NLTK 'averaged_perceptron_tagger' downloaded.")
        except Exception as e:
            self.logger.error(f"Error downloading NLTK 'averaged_perceptron_tagger': {e}")


    def __str__(self):
        return f"{Utils.__name__}"
    
    def saveFile(self, file_path, file_name, textToBeSaved, location_type="UNIX"):
        '''
            Save the text to a file at the specified file path and file name.
        '''
        try:
            # TODO: This method will be extended once GCS is added
            output_file_path = os.path.join(file_path , f"{file_name}.txt")
            self.logger.info(f"saveFile: file_name: {file_name}\n" \
                            f"output_file_path: {output_file_path}")
            with open(output_file_path, 'w') as file:
                file.writelines(textToBeSaved)
            # os.write(output_file_path, textToBeSaved, )# { encoding: 'utf-8' }
            return True
        except Exception as e:
            self.logger.error(f"saveFile: Error occurred while saving file: {e}")
            return False

    def getFile(self, file_path, file_name, location_type="UNIX"):
        '''
            Get the text from a file at the specified file path and file name.
        '''
        try:
            #  TODO: This method will be extended once GCS is added
            output_file_path = os.path.join(file_path , f"{file_name}.txt")
            self.logger.info(f"getFile: file_name: {file_name}" +
                            f"output_file_path: {output_file_path}");
            if (os.path.exists(output_file_path)):
                file = open(output_file_path, mode="r", encoding='utf-8')
                fileContents = file.read()
                # fileContents = os.read(outputFilePath, 'utf-8');
                return fileContents
            else:
                return f"Error: File does not exists"

        except Exception as e:
            self.logger.info(f"saveFile: Error occurred while saving file: {e}")
            return f"Error: {e}"

    # Hash the claim for caching
    def get_hash_value(self, value):
        return hashlib.sha256(value.encode()).hexdigest()
    
    def get_current_date(self):
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d")
    
    def get_current_time(self):
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")
    
    def get_current_date_time(self):
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    
    # generate chunks of text \ sentences <= 1024 tokens
    def extractive_tokenization(self, text, max_tokenizer_length=1024):
        '''
            generate array of sentences upto model max length allowed
        '''
        # self.logger.info(f"extractive_tokenization: Text: {len(text)}-{text}")
        nested = []
        sent = []
        length = 0
        for sentence in sent_tokenize(text):
            # TODO: Remove this logging
            self.logger.info(f"extractive_tokenization: Sentence: {len(sentence)}-{sentence}")
            length += len(sentence)
            if length < max_tokenizer_length:
                sent.append(sentence)
            else:
                nested.append(sent)
                # sent = []
                # length = 0
                sent = [ sentence ]
                length = len(sentence)

        if sent:
            nested.append(sent)
        # self.logger.info(f"extractive_tokenization: Nested: {len(nested)}-{nested}")

        return nested
    
    def abstractive_tokenization(self, tokenizer_input_text, max_tokenizer_length=1024):
        # get batches of tokens corresponding to the exact model_max_length
        # tokenizer_input_text will be an array
        # self.logger.debug(f"abstractive_tokenization: Text: {len(tokenizer_input_text)}-{tokenizer_input_text}")
        chunk_start = 0
        chunk_end = max_tokenizer_length
        inputs_batch_lst = []
        while chunk_start <= len(tokenizer_input_text[0]):
            inputs_batch = tokenizer_input_text[0][chunk_start:chunk_end]  # get batch of n tokens
            inputs_batch = torch.unsqueeze(inputs_batch, 0)
            inputs_batch_lst.append(inputs_batch)
            # chunk_start = chunk_end
            chunk_start += max_tokenizer_length
            chunk_end += max_tokenizer_length

        # self.logger.debug(f"abstractive_tokenization: Nested: {len(inputs_batch_lst)}-{inputs_batch_lst}")
        return inputs_batch_lst
    
    def parallel_tokenization(self, parallelize="N", tokenization_type = TokenizationType.ABSTRACTIVE_TOKENIZATION, tokenizer_input_text=None, max_tokenizer_length=1024):
        inputs_batch_lst = []
        if parallelize == "N":
            if tokenization_type == TokenizationType.ABSTRACTIVE_TOKENIZATION:
                inputs_batch_lst = self.abstractive_tokenization(tokenizer_input_text, max_tokenizer_length)
            else:
                inputs_batch_lst = self.extractive_tokenization(tokenizer_input_text, max_tokenizer_length)

        else:
            with multiprocessing.Pool(processes=ParallelizationNumbers.ONE) as pool:
                if tokenization_type == TokenizationType.ABSTRACTIVE_TOKENIZATION:
                    inputs_batch_lst = pool.map(self.abstractive_tokenization, tokenizer_input_text)
                else:
                    inputs_batch_lst = pool.map(self.extractive_tokenization, tokenizer_input_text)

        # self.logger.debug(f"parallel_tokenization: Nested: {len(inputs_batch_lst)}-{inputs_batch_lst}")
        return inputs_batch_lst
        # self.logger.debug(f"parallel_tokenization: Nested: {len(inputs_batch_lst)}-{inputs_batch_lst}")


