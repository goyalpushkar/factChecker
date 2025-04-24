import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { sha256 } from "js-sha256";
import { PropertiesReader } from "./readProperties"; // Assuming path
import Logger from "./Logger";
// import * as nltk from "nltk";
import natural from 'natural';
import { pipeline, Pipeline }  from '@xenova/transformers';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export enum ReturnTensorTypes {
  // # ExplicitEnum
  //
  // Possible values for the `return_tensors` argument in [`PreTrainedTokenizerBase.__call__`]. Useful for
  // tab-completion in an IDE.
  //
  PYTORCH = "pt",
  TENSORFLOW = "tf",
  NUMPY = "np",
  JAX = "jax",
  MLX = "mlx",
}

export enum AvailableLanguages {
    ENGLISH = "en",
    SPANISH = "es",
    FRENCH = "fr",
    GERMAN = "de",
    ITALIAN = "it",
    PORTUGUESE = "pt",
    DANISH = "da",
    HINDI = "hi"
}

export enum AvailableCountryCodes {
  US = "US",
  ENGLAND = "GB",
  SCOTLAND = "scotland",
  SOUTHAFRICA = "ZA",
  MEXICO = "MX",
  SPAIN = "ES",
  FRANCE = "FR",
  ITALY = "it",
  PORTUGAL = "pt",
  DENMARK = "dk",
  INDIA = "in",
}

export enum SummarizationTypes {
  // """
  // Possible values for the summarization types
  // """
  // # Summarization types
  EXTRACTIVE_SUMMARY = "extractive",
  ABSTRACTIVE_SUMMARY = "abstractive",
}

export enum TokenizationType {
  // """
  // Possible values for the summarization types
  // """
  // # Summarization types
  EXTRACTIVE_TOKENIZATION = "extractive",
  ABSTRACTIVE_TOKENIZATION = "abstractive",
}

export enum AvailableModels {
  // """
  // Possible values for the available models
  // """
  // # Available models
  T5_BASE = "t5-base",
  GOOGLE_PEGASUS = "google/pegasus-xsum",
  FACEBOOK_LARGECNN = "facebook/bart-large-cnn",
  PEGASUS_PARAPHRASE = "tuner007/pegasus_paraphrase",
  MICROSOFT_SPEECH = "microsoft/speecht5_tts",
  MICROSOFT_VOCODER = "microsoft/speecht5_hifigan",

  // # model.generate() method parameters -
  // # num_return_sequences  -> the possibility of generating multiple paraphrased sentences
  // # num_beams -> the number of beams for beam search. Setting it to 5 will allow the model
  // #  to look ahead for five possible words to keep the most likely hypothesis at each time step and choose the one that has the overall highest probability.
}

export enum SourceTypes {
  // """
  // Possible values for the caption sources
  // """
  // # source_types
  YOUTUBE = "youtube",
  VIDEO = "video",
  AUDIO = "audio",
  PODCAST = "podcast",
  WIKI = "wiki",
}

export enum CaptionSources {
  // """
  // Possible values for the caption types
  // """
  // # caption sources
  NLP = "nlp",
  THIRD_PARTY = "thirdparty",
  GOOGLE = "google",
  ALL = "all",
}

export enum TextToAudioSources {
  // """
  // Possible values for the audio from text sources
  // """
  // # audio text sources
  GTTS = "gtts",
  PYTTSX3 = "pyttsx3",
  OPENAI = "openai",
  TRANSFORMERS = "transformers",
  ALL = "all",
}

export enum SpeechSynthesizers {
  SAPI5 = "sapi5", //  # - SAPI5 on Windows
  NSSS = "nsss", //   # - NSSpeechSynthesizer on Mac OS X
  ESPEAK = "espeak", //  # - eSpeak on every other platform
}

export enum ParallelizationTypes {
  // """
  // Possible values for the parallelization types
  // """
  // # Parallelization types
  MULTI_PROCESSING = "multiprocessing",
  MULTI_THREADING = "multithreading",
  ASYNC = "async",
  SINGLE = "single",
}

export enum ParallelizationNumbers {
  // """
  // Possible values for the parallelization methods
  // """
  // # Parallelization methods
  // CPU_COUNT = multiprocessing.cpu_count(),
  // # GPU_COUNT = "gpu_count",
  ONE = 1,
  FOUR = 4,
  EIGHT = 8,
  SIXTEEN = 16,
  THIRTY_TWO = 32,
  HUNDRED_TWENTY_EIGHT = 128,
  TWO_HUNDRED_SIXTY_FOUR = 264,
}

export enum summarySelectedSize {
  SMALL = "small",
  MEDIUM = "medium",
  LARGE = "large",
  MARGIN = "margin",
}

// # Mapping of summary selected size to number of sentences
export enum SUMMARY_SIZE_MAPPING {
  SMALL = 800,
  MEDIUM = 1300,
  LARGE = 1800,
  MARGIN = 500,
}

// Define the type of the pipeline, for example 'sentiment-analysis'
// export type PipelineType = 'sentiment-analysis' | 'feature-extraction' | 'text-generation' | 'video-to-text';

// // Define the specific pipeline type
// export type MyPipeline = Pipeline<PipelineType>;

// export async function createPipeline(task: PipelineType, model?: string): Promise<MyPipeline> {
//   // Use the pipeline function with the specified task and optional model
//   const pipe = await pipeline(task, model);
//   return pipe as MyPipeline;
// }

class NltkLookupError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'NltkLookupError';
    Object.setPrototypeOf(this, NltkLookupError.prototype);
  }
}

export class Utils {
  private logger: Logger;
  private properties: PropertiesReader;

  constructor(kwargs?: any) {
    if (kwargs?.logger) {
      this.logger = kwargs.logger;
    } else {
      const loging = new Logger();
      this.logger = loging  //.getLogger();
    }

    if (kwargs?.properties) {
      this.properties = kwargs.properties;
    } else {
      this.properties = new PropertiesReader({ logger: this.logger });
    }

    //     # Use code with caution, suggested code may be subject to licenses
    //     # https://github.com/I4-Projektseminar-HHU-2017/i4-projekt-wissenstechnologien-got-mining
    //     # License unknownPowered by Gemini
    //     # Download necessary NLTK resources (only need to do this once)
  //   try{
  //       nltk.data.find('tokenizers/punkt')
  //   }catch (error){
  //     if (error instanceof NltkLookupError){
  //       nltk.download('punkt');
  //       nltk.download('punkt_tab');
  //       this.logger.info("NLTK 'punkt' tokenizer downloaded.");
  //   }else if (error instanceof Error){
  //       this.logger.error("Error downloading NLTK 'punkt': "+ error);
  //   }
  // }

  //   try{
  //     nltk.data.find('tokenizers/wordnet')
  //   }catch (error){
  //     if (error instanceof NltkLookupError){
  //       nltk.download('punkt')
  //       nltk.download('punkt_tab')
  //       this.logger.info("NLTK 'wordnet' tokenizer downloaded.")
  //   }else if (error instanceof Error){
  //       this.logger.error("Error downloading NLTK 'wordnet': "+ error);
  //   }
  // }

  //   try{
  //     nltk.data.find('corpora/stopwords')
  //   }catch (error){
  //     if (error instanceof NltkLookupError){
  //       nltk.download('punkt')
  //       nltk.download('punkt_tab')
  //       this.logger.info("NLTK 'stopwords' tokenizer downloaded.")
  //   }else if (error instanceof Error){
  //       this.logger.error("Error downloading NLTK 'stopwords': "+ error);
  //   }
  // }

  //   try{
  //     nltk.data.find('taggers/averaged_perceptron_tagger')
  //   }catch (error){
  //     if (error instanceof NltkLookupError){
  //       nltk.download('punkt')
  //       nltk.download('punkt_tab')
  //       this.logger.info("NLTK 'averaged_perceptron_tagger' tokenizer downloaded.")
  //   }else if (error instanceof Error){
  //       this.logger.error("Error downloading NLTK 'averaged_perceptron_tagger': "+ error);
  //   }
  // }
}

  // # Hash the claim for caching
  get_hash_value(value: string): string {
    const hash = sha256(value);
    return hash;
  }

  formatDate(date: Date, format: string): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0"); // Months are 0-indexed
    const day = String(date.getDate()).padStart(2, "0");

    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const seconds = String(date.getSeconds()).padStart(2, "0");

    if (format == "DATE") {
      return `${year}-${month}-${day}`;
    } else if (format == "TIME") {
      return `${hours}:${minutes}:${seconds}`;
    } else if (format == "DATETIME") {
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    }
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  }

  get_current_date(): string {
    const today = new Date();
    const formattedDate = this.formatDate(today, "DATE");
    return formattedDate; //datetime.datetime.now().strftime("%Y-%m-%d")
  }

  get_current_time(): string {
    const today = new Date();
    const formattedDate = this.formatDate(today, "TIME");
    return formattedDate; // %H:%M:%S"
  }

  get_current_date_time(): string {
    const today = new Date();
    const formattedDate = this.formatDate(today, "DATETIME");
    return formattedDate; //("%Y-%m-%d %H:%M:%S")
  }

  // # generate chunks of text \ sentences <= 1024 tokens
  extractive_tokenization(text: string, max_tokenizer_length = 1024): string[][] {
    //         '''
    //             generate array of sentences upto model max length allowed
    //         '''
    //         # self.logger.info(f"extractive_tokenization: Text: {len(text)}-{text}")
    const nested: string[][] = [];
    let sent: string[] = [];
    let length = 0;
    const sentTokenize = new natural.SentenceTokenizer([])
    for (const sentence of sentTokenize.tokenize(text)) {  // nltk.sent_tokenize
      //   # TODO: Remove this logging
      //   self.logger.info(f"extractive_tokenization: Sentence: {len(sentence)}-{sentence}")
      length += sentence.length;
      if (length < max_tokenizer_length) {
        sent.push(sentence);
      } else {
        nested.push(sent);
        // # sent = []
        // # length = 0
        sent = [sentence];
        length = sentence.length;
      }
    }

    if (sent.length > 0) {
      nested.push(sent);
    }
    // # self.logger.info(f"extractive_tokenization: Nested: {len(nested)}-{nested}")

    return nested;
  }

  abstractive_tokenization(tokenizer_input_text: any, max_tokenizer_length = 1024): any {
    // get batches of tokens corresponding to the exact model_max_length
    // tokenizer_input_text will be an array
    // self.logger.debug(f"abstractive_tokenization: Text: {len(tokenizer_input_text)}-{tokenizer_input_text}")
    let chunk_start = 0;
    let chunk_end = max_tokenizer_length;
    const inputs_batch_lst: any[] = [];
    while (chunk_start <= tokenizer_input_text[0].length) {
      const inputs_batch = tokenizer_input_text[0].slice(chunk_start, chunk_end); // get batch of n tokens
      //inputs_batch = torch.unsqueeze(inputs_batch, 0)
      inputs_batch_lst.push(inputs_batch);
      // chunk_start = chunk_end
      chunk_start += max_tokenizer_length;
      chunk_end += max_tokenizer_length;
    }

    // self.logger.debug(f"abstractive_tokenization: Nested: {len(inputs_batch_lst)}-{inputs_batch_lst}")
    return inputs_batch_lst;
  }

  parallel_tokenization(
    parallelize = "N",
    tokenization_type = TokenizationType.ABSTRACTIVE_TOKENIZATION,
    tokenizer_input_text: any = null,
    max_tokenizer_length = 1024
  ): any {
    let inputs_batch_lst: any[] = [];
    if (parallelize == "N") {
      if (tokenization_type == TokenizationType.ABSTRACTIVE_TOKENIZATION) {
        inputs_batch_lst = this.abstractive_tokenization(
          tokenizer_input_text,
          max_tokenizer_length
        );
      } else {
        inputs_batch_lst = this.extractive_tokenization(
          tokenizer_input_text,
          max_tokenizer_length
        );
      }
    } else {
      //   with multiprocessing.Pool(processes=ParallelizationNumbers.ONE) as pool:
      //       if tokenization_type == TokenizationType.ABSTRACTIVE_TOKENIZATION:
      //           inputs_batch_lst = pool.map(self.abstractive_tokenization, tokenizer_input_text)
      //       else:
      //           inputs_batch_lst = pool.map(self.extractive_tokenization, tokenizer_input_text)
    }

    // self.logger.debug(f"parallel_tokenization: Nested: {len(inputs_batch_lst)}-{inputs_batch_lst}")
    return inputs_batch_lst;
    // self.logger.debug(f"parallel_tokenization: Nested: {len(inputs_batch_lst)}-{inputs_batch_lst}")
  }
}