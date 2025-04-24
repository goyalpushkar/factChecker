import { PropertiesReader } from '@/lib/readProperties';
import { CaptionDerivationVideo } from './CaptionDerivationVideo';
import { CaptionDerivationAudio } from './CaptionDerivationAudio';
import Database from '@/lib/DB';
import Logger from '@/lib/Logger';
import {Utils, SourceTypes, CaptionSources} from '@/lib/utils';
import axios from 'axios';
import * as cheerio from 'cheerio';
import { Readability } from '@mozilla/readability';
import { JSDOM } from 'jsdom';

export class CaptionDerivation {
    private logger: Logger;
    private properties: PropertiesReader;
    private utils: Utils;
    private db: Database;
    private video_captions: CaptionDerivationVideo;
    private audio_captions: CaptionDerivationAudio;

    constructor(kwargs: any = null) {
        if (kwargs && kwargs.logger) {
            this.logger = kwargs.logger;
        } else {
            this.logger = new Logger();
            // this.logger = loging.log();
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
        this.video_captions = new CaptionDerivationVideo({ properties: this.properties, logger: this.logger });
        this.audio_captions = new CaptionDerivationAudio({ properties: this.properties, logger: this.logger });
    }

    toString(): string {
        return CaptionDerivation.name;
    }

    async get_captions(source_path: string, source_type: SourceTypes = SourceTypes.YOUTUBE, caption_source: CaptionSources = CaptionSources.ALL): Promise<any> {
        this.logger.info(`get_captions: Getting captions from ${source_path} using ${caption_source}`);
        if (source_type === SourceTypes.YOUTUBE || source_type === SourceTypes.VIDEO) {
            return this.get_video_captions(source_path, caption_source);
        }
        if (source_type === SourceTypes.PODCAST || source_type === SourceTypes.AUDIO) {
            return this.get_audio_captions(source_path, caption_source);
        }
    }

    async get_video_captions(video_path: string, caption_source: CaptionSources = CaptionSources.ALL): Promise<string | null> {
        this.logger.info(`get_video_captions: Getting captions from ${video_path} using ${caption_source}`);

        const video_id = this.video_captions.getVideoId(video_path);

        // Temporarily disable cache
        // const cached_result = await this.db.get_captions_cached_result(video_id);
        // if (cached_result) {
        //     return cached_result;
        // }

        let nlp_captions: string | null = null;
        let tp_captions: string | null = null;
        let google_captions: string | null = null;
        let final_caption: string = "";

        if (caption_source === CaptionSources.NLP) {
            nlp_captions = await this.video_captions.getCaptionsNlp(video_path);
            // if (nlp_captions) {
            //     this.db.insert_captions_cache(video_id, nlp_captions);
            // }
            return nlp_captions;
        } else if (caption_source === CaptionSources.THIRD_PARTY) {
            const tp_captions_data = await this.video_captions.getCaptionsThirdParty(video_path);
            let final_tp_captions = "";
            for (const data of tp_captions_data) {
                final_tp_captions += data.text || "";
                final_tp_captions += "";
            }
            tp_captions = final_tp_captions;

            // Temp Comment
            // if (tp_captions) {
            //     this.db.insert_captions_cache(video_id, tp_captions);
            // }

            return tp_captions;
        } else if (caption_source === CaptionSources.GOOGLE) {
            google_captions = await this.video_captions.getCaptionsGoogle(video_path);

            // Temp Comment
            // if (google_captions) {
            //     this.db.insert_captions_cache(video_id, google_captions);
            // }

            return google_captions;
        } else {
            try {
                nlp_captions = await this.video_captions.getCaptionsNlp(video_path);
            } catch (e: any) {
                this.logger.error(`Error getting captions: ${e.message}`);
            }

            if (!nlp_captions) {
                try {
                    const tp_captions_data = await this.video_captions.getCaptionsThirdParty(video_path);
                    let final_tp_captions = "";
                    for (const data of tp_captions_data) {
                        final_tp_captions += data.text || "";
                        final_tp_captions += "";
                    }
                    tp_captions = final_tp_captions;
                } catch (e: any) {
                    this.logger.error(`get_video_captions: Error getting captions: ${e.message}`);
                }
            }

            try {
                google_captions = await this.video_captions.getCaptionsGoogle(video_path);
            } catch (e: any) {
                this.logger.error(`Error getting captions: ${e.message}`);
            }

            this.logger.info(`get_video_captions: Captions: ${nlp_captions}, ${tp_captions}, ${google_captions}`);
            if (nlp_captions) {
                final_caption = nlp_captions;
            } else if (tp_captions) {
                final_caption = tp_captions;
            } else if (google_captions) {
                final_caption = google_captions;
            } else {
                final_caption = "";
            }

            this.logger.info(`get_video_captions: Captions: ${final_caption}`);
            // if (final_caption !== "") {
            //     this.db.insert_captions_cache(video_id, final_caption);
            // }
        }

        return final_caption;
    }

    async get_audio_captions(audio_path: string, caption_source: CaptionSources = CaptionSources.ALL): Promise<string> {
        this.logger.info(`get_audio_captions: Getting captions from ${audio_path} using ${caption_source}`);

        const audio_id = this.audio_captions.getAudioId(audio_path);

        return "";
    }

    async get_wiki_captions(source_path: string): Promise<string | null> {
        this.logger.info(`get_wiki_captions: source_path: ${source_path}`);
        if (source_path.startsWith("https://en.wikipedia.org/wiki/")) {
            return this.get_wiki_url_text(source_path);
        } else {
            return this.get_web_captions(source_path);
        }
    }

    private get_full_body_text(html_content: string): string | null {
        try {
            const $ = cheerio.load(html_content);
            const body = $('body');
            if (body.length) {
                body.find('script, style').remove();
                const text = body.text().replace(/\s+/g, ' ').trim();
                this.logger.info(`get_full_body_text: Successfully extracted primary content (length: ${text.length})`);
                return text;
            } else {
                const text = $.text().replace(/\s+/g, ' ').trim();
                this.logger.info(`get_full_body_text: Successfully extracted primary content (length: ${text.length})`);
                return text;
            }
        } catch (e: any) {
            this.logger.error(`_get_full_body_text: Error in fallback text extraction: ${e.message}`);
            return null;
        }
    }

    async get_web_captions(source_path: string): Promise<string | null> {
        try {
            this.logger.info(`get_web_captions: source_path: ${source_path}`);

            const headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            };

            const response = await axios.get(source_path, { headers, timeout: 30000 });
            response.data
            const dom = new JSDOM(response.data, { url: source_path });
            const reader = new Readability(dom.window.document);
            const article = reader.parse();
            this.logger.info(`get_web_captions: article: ${article}`);

            if (article) {
                this.logger.info(`get_web_captions: Successfully extracted primary content from ${source_path} - (length: ${article.textContent!.length})`);
                return article.textContent!.replace(/\s+/g, ' ').trim();
            } else {
                this.logger.warn(`get_web_captions: Readability found no primary content in ${source_path}. Falling back to full body text.`);
                return this.get_full_body_text(response.data);
            }
        } catch (e: any) {
            if (e.code === 'ECONNABORTED') {
                this.logger.error(`get_web_captions: Request timed out for URL: ${source_path}`);
            } else {
                this.logger.error(`get_web_captions: Error fetching URL ${source_path}: ${e.message}`);
            }
            return null;
        }
    }

    async get_wiki_url_text(wiki_url: string): Promise<string | null> {
        try {
            this.logger.info(`get_wiki_url_text: wiki_url: ${wiki_url}`);

            const response = await axios.get(wiki_url);
            const $ = cheerio.load(response.data);
            this.logger.info(`get_wiki_url_text: response: ${response.data}`);

            const main_content = $('#mw-content-text');
            let text_content = "";
            if (main_content.length) {
                const paragraphs = main_content.find("p");
                text_content = paragraphs.toArray().map(p => $(p).text()).join("\n");
            }
            this.logger.info(`get_wiki_url_text: text_content: ${text_content}`);
            return text_content;
        } catch (e: any) {
            this.logger.error(`get_wiki_url_text: Error: ${e.message}`);
            return null;
        }
    }
}