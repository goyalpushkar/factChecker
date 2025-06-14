# Import necessary libraries
from source.services.lib.readProperties import PropertiesReader
from source.services.lib.DB import Database
from source.services.lib.Logger import Logger 
from source.services.lib.utils import Utils, TokenizationType, AvailableModels, ReturnTensorTypes, AvailableLanguages, TextToAudioSources, SpeechSynthesizers, AvailableCountryCodes
from transformers import pipeline
import torch
import os
import multiprocessing

from playsound import playsound


# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TextToAudio:
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


        self.db = Database(kwargs={"logger":self.logger})

        # model_max_length is in token space not character space – len(text) != len(tokenizer(text))
        # tokenizer.model_max_length
        # T5 a priori, since its max input length is 512, while Bart and Pegasus can be fed with max 1024 tokens.
        self.max_tokenizer_length = 1024  # tokenizer.model_max_length
        self.speech_model_length = 600
        if torch.cuda.is_available():
            self.device = 'cuda'
            self.logger.info("CUDA is available. Using GPU for Transformers TTS.")
        else:
            self.device = 'cpu'
            self.logger.info("CUDA not available. Using CPU for Transformers TTS.")

        self.tensor_return_type = ReturnTensorTypes.PYTORCH

        self.model_name = AvailableModels.MICROSOFT_SPEECH
        self.vocoder = AvailableModels.MICROSOFT_VOCODER
        self.speaker_datasets = "Matthijs/cmu-arctic-xvectors"
        # speaker ids from the embeddings dataset
        self.speakers = {
                    'awb': 0,     # Scottish male
                    'bdl': 1138,  # US male
                    'clb': 2271,  # US female
                    'jmk': 3403,  # Canadian male
                    'ksp': 4535,  # Indian male
                    'rms': 5667,  # US male
                    'slt': 6799   # US female
                }
        self.speaker = self.speakers['awb']
        
    def __str__(self):
        return f"{TextToAudio.__name__}"
    

    def getAudio(self, text, source=TextToAudioSources.GTTS, language=AvailableLanguages.ENGLISH, countryCode=AvailableCountryCodes.US, action=1):
        """
        Extracts potential factual statements from a given text."
        """
        # TODO - 
        # This maynot be worth the effort 
        # Add DB caching to get audio for similar text 
        #   DB will have hashkey for text and corresponding audio file path 
        # Audio files can be saved in partitioned disk by date and time 
        #   so it will be easier for retrieval
        if source == TextToAudioSources.GTTS:
            audio = self.getAudioGtts(text, language, countryCode)
        elif source == TextToAudioSources.PYTTSX3:
            audio = self.getAudioPyttsx3(text, language, countryCode, action)
        elif source == TextToAudioSources.TRANSFORMERS:
            audio = self.getAudioTramsformers(text, language, countryCode)
        else:
            audio_gtts = self.getAudioGtts(text, language)
            audio_pyttsx = self.getAudioPyttsx3(text, language, action)
            audio_transformers = self.getAudioTramsformers(text, language)
            audio = ""
            if audio_gtts is not None and audio_gtts != "":
                audio = audio_gtts
            elif audio_pyttsx is not None and audio_pyttsx != "":
                audio = audio_pyttsx
            elif audio_transformers is not None and audio_transformers != "":
                audio = audio_transformers

        return audio
    
    def get_file_name(self, text, model_name, extension="mp3"):
        """
        Get the file name for the audio file
        """
        current_date = self.utils.get_current_date()
        hashed_val = self.utils.get_hash_value(text[:8]+model_name)
        
        # Get the folder name from the properties
        folder_name = self.properties.get_property("folders", "audio_directory")
        file_name = str(current_date) + "_" + str(hashed_val) + "." + extension

        folder_file = folder_name+file_name

        return folder_file
    
    def get_file_without_folder_name(self, file_name, target_dir="audioFilesDirectory"):
        """
        Get the file name for the audio file
        """
        # to send path from target_dir=audioFilesDirectory folder onwards
        # relative_path = file_name[file_name.find(target_dir):]
        
        # Normalize the path first (handles mixed separators, redundant slashes)
        norm_path = os.path.normpath(file_name)

        parts = norm_path.split(os.sep) # Split by the OS-specific separator

        relative_path = None
        try:
            # Find the index of the target directory
            target_index = parts.index(target_dir)
            # Join the parts from the target directory onwards
            relative_path = os.path.join(*parts[target_index:])
            # Optional: Normalize separators for URL consistency
            relative_path = relative_path.replace("\\", "/")

            return relative_path
        
        except ValueError:
            print(f"'{target_dir}' not found in path components.")

    
    def getAudioGtts(self, text, language=AvailableLanguages.ENGLISH, countryCode=AvailableCountryCodes.US):
        """
        Get audio using gtts
        This needs internet connection and works only online
        """
        try:
            import gtts

            self.logger.info(f"getAudioGtts: Getting audio from {text} using gtts in {language}")
            tts = gtts.gTTS(text, lang=language)
            # self.logger.info(f"getAudioGtts: Languages: {len(gtts.lang.tts_langs())}")

            folder_file = self.get_file_name(text, TextToAudioSources.GTTS)
            self.logger.info(f"getAudioGtts: Saving audio to {folder_file}")
            
            # Save the audio to a file
            tts.save(folder_file)
            self.logger.info(f"getAudioGtts: Audio saved at {folder_file}")

            return folder_file

        except Exception as e:
            self.logger.error(f"getAudioGtts: Error getting audio: {e}")
            return None
    
    # https://thepythoncode.com/article/convert-text-to-speech-in-python 
    def getAudioPyttsx3(self, text, language=AvailableLanguages.ENGLISH, countryCode=AvailableCountryCodes.US, action=1):
        """
            Get audio using pyttsx3
            This works offline

            This file is playable with quick time player but somehow not playing with
            apple music. Identified that there are diffrent drivers for each operating system
            sapi5 - SAPI5 on Windows
            nsss - NSSpeechSynthesizer on Mac OS X
            espeak - eSpeak on every other platform
            Even after changing the driver it is not generating the file that can be playable on web
            It works only with QuickTime player
        """
        try:
            import pyttsx3
            import platform
            self.logger.info(f"getAudioPyttsx3: Getting audio from {text} using pyttsx3 in {language}")

            # 'Windows' for Windows.
            # 'Linux' for Linux.
            # 'Darwin' for macOS.
            if platform.system() == "Windows":
                driverName = SpeechSynthesizers.SAPI5
            elif platform.system() == "Linux":
                driverName = SpeechSynthesizers.ESPEAK
            elif platform.system() == "Darwin": # macOS
                driverName = SpeechSynthesizers.NSSS
            else:   
                driverName = SpeechSynthesizers.ESPEAK
            self.logger.info(f"getAudioPyttsx3: Driver Name: {driverName}")

            # Initialize the pyttsx3 engine driverName=driverName
            engine = pyttsx3.init(driverName=driverName)

            # Setting voice for the engine
            voices = engine.getProperty('voices')
            voice_set = 0
            for voice in voices:
                self.logger.info(f"getAudioPyttsx3: Voice: Name: {voice.name}\n "
                                    f"ID: {voice.id}\n"
                                    f"age: {voice.age}\n"
                                    f"gender: {voice.gender}\n"
                                    f"languages: {voice.languages}\n")
                # Give preference to female voice
                if voice.languages and language+"_"+countryCode in voice.languages and voice.gender == "VoiceGenderFemale":
                    engine.setProperty('voice', voice.id)
                    voice_set = 1
                    break
                elif voice.languages and language+"_"+countryCode in voice.languages :
                    engine.setProperty('voice', voice.id)
                    voice_set = 1
                # else:
            
            # if language is not supported by the engine
            if voice_set == 0:
                self.logger.info(f"getAudioPyttsx3: Language is not supported so setting default voice")
                # If the language is not supported, use the default voice
                engine.setProperty('voice', voices[0].id)
                self.logger.info(f"getAudioPyttsx3: Voice: Name: {voices[0].name}")                
            
            # Get file name for the audio file
            folder_file = self.get_file_name(text, TextToAudioSources.PYTTSX3, extension="wav")
            self.logger.info(f"getAudioPyttsx3: Saving audio to {folder_file}")

            # adds an utterance to speak to the event queue
            if action == 1:
                # engine.say(text)
                # Save the audio to a file
                engine.save_to_file(text, folder_file)
            else:
                engine.stop()
                return None

            # The pyttsx3 engine is designed to run its event loop once to process all queued commands 
            # (say, save_to_file, etc.). Calling runAndWait() starts this loop. If you call it again 
            # before the first loop has properly finished and the engine state is reset (which doesn't 
            # happen automatically here), you get this error.
            # # runs the actual event loop until all commands are queued up
            # engine.runAndWait()

            # get details of speaking rate
            # rate = engine.getProperty("rate")
            # self.logger.info(f"getAudioPyttsx3: rate: {rate}")

            # # get details of all voices available
            # voices = engine.getProperty("voices")
            # self.logger.info(f"getAudioPyttsx3: {voices}")

            engine.runAndWait()
            self.logger.info(f"getAudioPyttsx3: Audio saved at {folder_file}")

            return folder_file

        except ImportError as e:
            self.logger.error(f"getAudioPyttsx3: Error importing pyttsx3: {e}")
            return None
        except RuntimeError as e:
            self.logger.error(f"getAudioPyttsx3: Error initializing pyttsx3: {e}")
            return None
        except Exception as e:
            self.logger.error(f"getAudioPyttsx3: Error getting audio: {e}")
            return None
        # finally:    
            # Remove the engine.stop() and engine.endLoop() calls from the finally block when using runAndWait().
            # The runAndWait() function handles the loop's lifecycle completely – it starts, processes 
            # queued commands, and stops the loop automatically upon completion. Explicitly trying to stop or 
            # end it again afterwards is incorrect.
            # Self Findings - If we call the method again it gives error "run loop already started" that is 
            # loop is not getting closed or end until we do it in finally
            # engine.stop()
            # engine.endLoop()

    def getAudioTramsformers(self, text, language=AvailableLanguages.ENGLISH, countryCode=AvailableCountryCodes.US):
        """
            Get audio using transformers
            This will work good for smaller texts but for larger texts this will take a lot of time
            to do tensor procesing and in that process it will loose some of the text too
        """
        try:
            self.logger.info(f"getAudioTramsformers: Getting audio from {text} using transformers in {language}")

            from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
            from datasets import load_dataset
            import random
            import string
            import soundfile as sf

            # load the processor
            processor = SpeechT5Processor.from_pretrained(self.model_name)

            # load the model
            model = SpeechT5ForTextToSpeech.from_pretrained(self.model_name).to(self.device)

            # load the vocoder, that is the voice encoder
            vocoder = SpeechT5HifiGan.from_pretrained(self.vocoder).to(self.device)

            # we load this dataset to get the speaker embeddings
            embeddings_dataset = load_dataset(self.speaker_datasets, split="validation")
            self.logger.info(f"getAudioTramsformers: Embeddings dataset: {embeddings_dataset}")

            # preprocess text
            inputs = processor(text=text, return_tensors=self.tensor_return_type).to(self.device)
            self.logger.info(f"abstractive_summarization_abstract_tokens: Inputs: {len(inputs['input_ids'][0])}-{inputs}")
            
            # Generate list of tokens based on max model length
            inputs_batch_list = self.utils.parallel_tokenization(parallelize="N", tokenization_type=TokenizationType.ABSTRACTIVE_TOKENIZATION, tokenizer_input_text=inputs['input_ids'],
                                                                max_tokenizer_length=self.speech_model_length)
            self.logger.info(f"getAudioTramsformers: inputs_batch_list: {len(inputs_batch_list)}-{inputs_batch_list}")
            
            if self.speaker is not None:
                # load xvector containing speaker's voice characteristics from a dataset
                speaker_embeddings = torch.tensor(embeddings_dataset[self.speaker]["xvector"]).unsqueeze(0).to(self.device)
            else:
                # random vector, meaning a random voice
                speaker_embeddings = torch.randn((1, 512)).to(self.device)
            # speaker_embeddings_list = self.utils.parallel_tokenization(parallelize="N", tokenization_type=TokenizationType.ABSTRACTIVE_TOKENIZATION, tokenizer_input_text=speaker_embeddings,
            #                                                      max_tokenizer_length=self.speech_model_length)
            # self.logger.info(f"getAudioTramsformers: speaker_embeddings_list: {len(speaker_embeddings_list)}-{speaker_embeddings_list}")

            
            # generate speech with the models
            # speech = model.generate_speech(inputs_batch_list, speaker_embeddings, vocoder=vocoder)

             # Generate Summary, output will be a tensor format
            speech_list = []
            for input in inputs_batch_list:
                # TODO - Remove after testing. This is added for debugging purpose
                self.logger.debug(f"getAudioTramsformers: Input: {len(input)}-{input}")

                speeches = model.generate_speech(input, speaker_embeddings, vocoder=vocoder)
                speech_list.append(speeches)
            # speech_list = [model.generate_speech(input, speaker_embeddings, vocoder=vocoder) 
            #                for input in inputs_batch_list ]  #  argument after ** must be a mapping, not list
            self.logger.debug(f"getAudioTramsformers: speech_list: {len(speech_list)}-{speech_list}")
            
            # summarized_text = [[tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summary_ids] for summary_ids in inputs_batch_list]
            # self.logger.info(f"paraphrase_text summarized_text: {len(summarized_text)}-{summarized_text}")
            
            if speech_list:
                # Concatenate all segments efficiently along the time dimension (usually dim=0 for 1D audio)
                speech = torch.cat(speech_list, dim=0)
                self.logger.info(f"getAudioTramsformers: Concatenated speech tensor shape: {speech.shape}")

                # generate a random filename
                folder_file = self.get_file_name(text, TextToAudioSources.TRANSFORMERS)
                self.logger.info(f"getAudioTramsformers: Saving audio to {folder_file}")
                
                # save the generated speech to a file with 16KHz sampling rate
                sf.write(folder_file, speech.cpu().numpy(), samplerate=16000)
                self.logger.info(f"getAudioTramsformers: Audio Saved at {folder_file}")

                # return the filename for reference
                return folder_file
            else:
                return None
            
        except ImportError as e:
            self.logger.error(f"getAudioTramsformers: Missing required library: {e}. Please install transformers, datasets, torch, soundfile.")
            return None
        except Exception as e:
            self.logger.error(f"getAudioTramsformers: Error getting audio: {e}")
            return None