import { PropertiesReader } from '@/lib/readProperties'; // Assuming path
import { Utils } from '@/lib/utils'; // Assuming path
import Database from '@/lib/DB'; // Assuming path
import Logger from '@/lib/Logger'; // Assuming path

export class CaptionDerivationAudio {
    private logger: Logger;
    private properties: PropertiesReader;
    private utils: Utils;
    private db: Database;

    constructor(kwargs?: { logger?: Logger; properties?: PropertiesReader; utils?: Utils }) {
        if (kwargs && kwargs.logger) {
            this.logger = kwargs.logger;
        } else {
            this.logger = new Logger();
            // this.logger = logging.getLogger();
        }

        if (kwargs && kwargs.properties) {
            this.properties = kwargs.properties;
        } else {
            this.properties = new PropertiesReader({ logger: this.logger });
        }

        if (kwargs && kwargs.utils) {
            this.utils = kwargs.utils;
        } else {
            this.utils = new Utils({ logger: this.logger, properties: this.properties });
        }

        this.db = new Database({ logger: this.logger });
    }

    toString(): string {
        return CaptionDerivationAudio.name;
    }

    getAudioId(audioPath: string): string {
        let audioId = audioPath.split("=").pop();
        if (!audioId) {
            audioId = audioPath.split("/").pop();
        }
        return audioId || ""; // Return empty string if still undefined
    }

    getCaptions(audioPath: string, source: string = "all"): void {
        /*
            Get captions from the audio.
        */
        this.logger.log(`get_captions: Getting captions from ${audioPath} using ${source}`);
    }
}