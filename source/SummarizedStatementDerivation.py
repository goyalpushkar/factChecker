# Import necessary libraries
from readProperties import PropertiesReader
from DB import Database
from Logger import Logger 
import multiprocessing
from utils import Utils, SummarizationTypes, AvailableModels, ReturnTensorTypes, ParallelizationNumbers, TokenizationType
from transformers import pipeline
from transformers.pipelines.pt_utils import KeyDataset
import datasets

# genism
# from gensim.summarization.summarizer import summarize
# from gensim.summarization import keywords
import en_core_web_sm

import torch 
from transformers import AutoTokenizer, AutoModelWithLMHead, AutoModelForSeq2SeqLM, PegasusForConditionalGeneration, PegasusTokenizer, BartTokenizer

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag

# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SummarizedStatementDerivation:
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

        # model_max_length is in token space not character space – len(text) != len(tokenizer(text))
        # tokenizer.model_max_length
        # T5 a priori, since its max input length is 512, while Bart and Pegasus can be fed with max 1024 tokens.
        self.max_tokenizer_length = 1024  # tokenizer.model_max_length
        self.max_paraphrase_tokenizer_length = 60
        self.device = 'cuda'
        self.tensor_return_type = ReturnTensorTypes.PYTORCH

        self.model_name = AvailableModels.FACEBOOK_LARGECNN
        self.paraphrase_model_name = AvailableModels.PEGASUS_PARAPHRASE

        
    def __str__(self):
        return f"{SummarizedStatementDerivation.__name__}"
    
    def get_summarized_statements(self, text, summary_type=SummarizationTypes.ABSTRACTIVE_SUMMARY):
        """
        Extracts potential factual statements from a given text."
        """
        summarized_text = self.extractive_summarization(text) if summary_type == SummarizationTypes.EXTRACTIVE_SUMMARY \
            else self.abstractive_summarization_abstract_tokens(text)
        final_text = self.paraphrase_text(summarized_text)
        self.logger.info(f"get_summarized_statements: {len(final_text)}-{final_text}")
        return final_text
    
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
    
    def parallel_tokenization(self, tokenization_type = TokenizationType.ABSTRACTIVE_TOKENIZATION, tokenizer_input_text=None, max_tokenizer_length=1024):
        # with multiprocessing.Pool(processes=ParallelizationNumbers.ONE) as pool:
        #     if tokenization_type == TokenizationType.ABSTRACTIVE_TOKENIZATION:
        #         inputs_batch_lst = pool.map(self.abstractive_tokenization, tokenizer_input_text)
        #     else:
        #         inputs_batch_lst = pool.map(self.extractive_tokenization, tokenizer_input_text)

        if tokenization_type == TokenizationType.ABSTRACTIVE_TOKENIZATION:
            inputs_batch_lst = self.abstractive_tokenization(tokenizer_input_text, max_tokenizer_length)
        else:
            inputs_batch_lst = self.extractive_tokenization(tokenizer_input_text)

        # self.logger.debug(f"parallel_tokenization: Nested: {len(inputs_batch_lst)}-{inputs_batch_lst}")
        return inputs_batch_lst
        # self.logger.debug(f"parallel_tokenization: Nested: {len(inputs_batch_lst)}-{inputs_batch_lst}")

    def extractive_summarization(self, text):
        """
            Get extractive summay text using the
            sumy, gensim, summa, bert-extractive-summarizer, etc.
        """
        try:
            # gensim
            # Summarize based on Percentage
            # summ_per = summarize(text, ratio = "")
            # self.logger.info("Percent summary")
            # self.logger.info(summ_per)
            
            # # Summarize based on word count 
            # summ_words = summarize(text, word_count = "")
            # self.logger.info("Word count summary")
            # self.logger.info(summ_words)
            
            # Summarize based on sentences
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelWithLMHead.from_pretrained(self.model_name, return_dict=True)

            # successive abstractive summarisation - Divide the text into max allowed length, 
            # do summary on each part and then again use it to summarise till the length you want. 
            sentences = self.extractive_summarization(text)
            self.logger.info(f"abstractive_summarization_online: Number of sentences: {len(sentences)}")

            inputs = tokenizer.encode("summarize: " + text,
                                    return_tensors=self.tensor_return_type,
                                    max_length=512,
                                    truncation=True)

            summary_ids = model.generate(inputs, max_length=150, min_length=80, length_penalty=5., num_beams=2)  
            summarized_text = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            self.logger.info("Sentence summary")
            self.logger.info(summarized_text)
            
            return summarized_text
        except Exception as e:
            self.logger.error(f"Error getting summarized_text: {e}")
            return None
        
    def abstractive_summarization_abstract_tokens(self, text):
        """
            Get abstractive summay text using the Hugging Face pipeline.
            transformers (Hugging Face) - using models like BART, T5, Pegasus.
            abstractive summary using abstractive tokenization 
            i.e. divide the token list from huge text into model_max_length array of tokens
        """
        try:
            self.logger.info(f"abstractive_summarization_abstract_tokens: Get summarized_text using {self.model_name} for Text: {len(text)}-{text}")
        
            # Load the model and tokenizer
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            summarizer = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            # summarizer = pipeline("summarization", model=self.model_name, tokenizer=tokenizer, truncation=True, device=self.device)
            # , max_length=1024

            # Replace huge text with the text you want to summarize
            # pipe = pipeline("text2text-generation", model=summarizer, tokenizer=tokenizer, device=self.device)
            # generated_text = pipe(
            #     text, 
            #     truncation=True, 
            #     max_length=2048, 
            #     no_repeat_ngram_size=5, 
            #     num_beams=3, 
            #     early_stopping=True
            #     )
            # self.logger.info(f"abstractive_summarization_online: generated_text: {len(generated_text)}-{generated_text}")
        
            # Tokenize the text, output will be a tensor format
            inputs = tokenizer([text], return_tensors=self.tensor_return_type)
            # max_length=self.max_tokenizer_length, use_fast = 'False'
            self.logger.info(f"abstractive_summarization_abstract_tokens: Inputs: {len(inputs['input_ids'])}-{inputs}")
            # error with max_length=4096 IndexError: index out of range in self

            # Generate list of tokens based on max model length
            inputs_batch_list = self.parallel_tokenization(tokenization_type=TokenizationType.ABSTRACTIVE_TOKENIZATION, tokenizer_input_text=inputs['input_ids'], max_tokenizer_length=self.max_tokenizer_length)
            self.logger.debug(f"abstractive_summarization_abstract_tokens: Nested: {len(inputs_batch_list)}-{inputs_batch_list}")

            # Generate Summary, output will be a tensor format
            summary_id_list = [summarizer.generate(input, num_beams=4, max_length=500, early_stopping=False) for input in inputs_batch_list]
            self.logger.info(f"abstractive_summarization_abstract_tokens: summary_id_list: {len(summary_id_list)}-{summary_id_list}")
            
            # Decode Summarized text for each summary
            summarized_text = [[tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summary_ids] for summary_ids in summary_id_list]
            self.logger.info(f"abstractive_summarization_abstract_tokens summarized_text: {len(summarized_text)}-{summarized_text}")
            
            final_summary = ""
            for text in summarized_text:
                final_summary += text[0]
            # # dataset = text.map(lambda text: tokenize_dataset(tokenizer, text), batched=True)
            # summarized_text = summarizer(text, max_length=130, min_length=30, do_sample=False)
            # self.logger.info(f"abstractive_summarization: Summarized Text: {summarized_text}")
            # final_summary = summarized_text[0]['summary_text']

            self.logger.info(f"abstractive_summarization_abstract_tokens: final_summary: {len(final_summary)}-{final_summary}")
            return final_summary

        except Exception as e:
            self.logger.error(f"abstractive_summarization_abstract_tokens: Error getting summarized_text: {e}")
            return None
        
    def abstractive_summarization_extract_tokens(self, text):
        """
            abstractive summary using extractive tokenization 
            i.e. divide the text into model_max_length array of text
            This could be a problematic because model_max_length is length of tokens
            which will not be same as the length of text
        """
        try:
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            summarizer = pipeline("summarization", model=self.model_name, tokenizer=tokenizer, device=self.device)
                # , max_length=1024 , truncation=True

            sentences_list = self.parallel_tokenization(tokenization_type=TokenizationType.EXTRACTIVE_TOKENIZATION, tokenizer_input_text=text, max_tokenizer_length=self.max_tokenizer_length)
            self.logger.info(f"abstractive_summarization_extract_tokens: {len(sentences_list)}-{sentences_list}")
            summaries = []
            for sentences in sentences_list:
                input_tokenized = tokenizer.encode(' '.join(sentences), return_tensors=self.tensor_return_type) # , truncation=True
                input_tokenized = input_tokenized.to(self.device)
                summary_ids = summarizer.to(self.device).generate(input_tokenized,
                                                                length_penalty=3.0,
                                                                min_length=30,
                                                                max_length=120)
                summarized_text = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summary_ids]
                self.logger.info(f"abstractive_summarization_extract_tokens: {len(summarized_text)}-{summarized_text}")
                
                summaries.append(summarized_text)

            final_summary = [sentence for sublist in summaries for sentence in sublist]
            self.logger.info(f"abstractive_summarization_extract_tokens: {len(final_summary)}-{final_summary}")
            return final_summary[0]
        except Exception as e:
            self.logger.error(f"abstractive_summarization_extract_tokens: Error getting summarized_text: {e}")
            return None
        
    def paraphrase_text(self, text):
        """
            Paraphrase the text using the Hugging Face pipeline.
        """
        try:
            self.logger.info(f"paraphrase_text: Get summarized_text using {self.paraphrase_model_name} for Text: {len(text)}-{text}")
        
            # Load the model and tokenizer
            tokenizer = PegasusTokenizer.from_pretrained(self.paraphrase_model_name)
            paraphraser = PegasusForConditionalGeneration.from_pretrained(self.paraphrase_model_name)

            # Replace huge text with the text you want to summarize
            # pipe = pipeline("text2text-generation", model=summarizer, tokenizer=tokenizer, device=self.device)
            # generated_text = pipe(
            #     text, 
            #     truncation=True, 
            #     max_length=2048, 
            #     no_repeat_ngram_size=5, 
            #     num_beams=3, 
            #     early_stopping=True
            #     )
            # self.logger.info(f"abstractive_summarization_online: generated_text: {len(generated_text)}-{generated_text}")
        
            # Tokenize the text, output will be a tensor format
            inputs = tokenizer([text], return_tensors=self.tensor_return_type) # max_length=self.max_tokenizer_length, 
            self.logger.info(f"paraphrase_text: Inputs: {len(inputs['input_ids'])}-{inputs}")
            # error with max_length=4096 IndexError: index out of range in self

            # Generate list of tokens based on max model length
            inputs_batch_list = self.parallel_tokenization(tokenization_type=TokenizationType.ABSTRACTIVE_TOKENIZATION, tokenizer_input_text=inputs['input_ids'], max_tokenizer_length=self.max_paraphrase_tokenizer_length)
            self.logger.debug(f"paraphrase_text: Nested: {len(inputs_batch_list)}-{inputs_batch_list}")

            # Generate Summary, output will be a tensor format
            summary_id_list = [paraphraser.generate(input, num_beams=4, max_length=500, early_stopping=False) for input in inputs_batch_list ]  #  argument after ** must be a mapping, not list
            self.logger.info(f"paraphrase_text: summary_id_list: {len(summary_id_list)}-{summary_id_list}")
            
            # Decode Summarized text for each summary
            summarized_text = [[tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summary_ids] for summary_ids in summary_id_list]
            self.logger.info(f"paraphrase_text summarized_text: {len(summarized_text)}-{summarized_text}")
            
            final_summary = ""
            for text in summarized_text:
                final_summary += text[0]
            # # dataset = text.map(lambda text: tokenize_dataset(tokenizer, text), batched=True)
            # summarized_text = summarizer(text, max_length=130, min_length=30, do_sample=False)
            # self.logger.info(f"abstractive_summarization: Summarized Text: {summarized_text}")
            # final_summary = summarized_text[0]['summary_text']

            self.logger.info(f"paraphrase_text: final_summary: {len(final_summary)}-{final_summary}")
            return final_summary

        except Exception as e:
            self.logger.error(f"paraphrase_text: Error getting summarized_text: {e}")
            return None