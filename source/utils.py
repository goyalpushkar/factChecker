
from readProperties import PropertiesReader
from Logger import Logger
import multiprocessing
# from transformers import utils.ExplicitEnum

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

    def __str__(self):
        return f"{Utils.__name__}"
    
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
    ALL = "all"

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
    FOUR = 4
    EIGHT = 8
    SIXTEEN = 16
    THIRTY_TWO = 32
    HUNDRED_TWENTY_EIGHT = 128
    TWO_HUNDRED_SIXTY_FOUR = 264