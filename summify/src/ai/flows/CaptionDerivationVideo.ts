import { pipeline, Pipeline }  from '@xenova/transformers';
// import { YoutubeTranscriptApi } from 'youtube-transcript-api';
import { YoutubeTranscript } from 'youtube-transcript';
import { PropertiesReader } from '@/lib/readProperties'; // Assuming path
import { Utils } from '@/lib/utils'; // Assuming path
import Database from '@/lib/DB'; // Assuming path
import Logger from '@/lib/Logger'; // Assuming path
import { Authorization } from '@/lib/Authorization';  // Assuming path
import { youtube_v3 } from '@googleapis/youtube';

export class CaptionDerivationVideo {
    private logger: Logger;
    private properties: PropertiesReader;
    private utils: Utils;
    private db: Database;
    private authorization: Authorization;

    constructor(kwargs?: any) {
        if (kwargs?.logger) {
            this.logger = kwargs.logger;
        } else {
            this.logger = new Logger();
            // this.logger = loging.getLogger();
        }

        if (kwargs?.properties) {
            this.properties = kwargs.properties;
        } else {
            this.properties = new PropertiesReader({ logger: this.logger });
        }

        if (kwargs?.utils) {
            this.utils = kwargs.utils;
        } else {
            this.utils = new Utils({ logger: this.logger, properties: this.properties });
        }

        this.db = new Database({ logger: this.logger });
        this.authorization = new Authorization({ properties: this.properties, logger: this.logger });
    }

    toString(): string {
        return CaptionDerivationVideo.name;
    }

    getVideoId(videoPath: string): string {
        let videoId = videoPath.split("=").pop();
        if (!videoId) {
            videoId = videoPath.split("/").pop();
        }
        return videoId || ""; // Ensure a string is returned
    }

    getCaptionsYtDlp(videoPath: string): string {
        return "";
    }

    async getCaptionsNlp(videoPath: string): Promise<any | null> {
        try {
            // TODO: Download the video or audio from the URL
            // const nlp = await pipeline("video-to-text", 'Xenova/whisper-small');
            // const captions = await nlp(videoPath);
            // return captions;
            return null;
        } catch (error: any) {
            this.logger.error(`Error getting captions: ${error}`);
            return null;
        }
    }

    async getCaptionsThirdParty(videoPath: string): Promise<any | null> {
        try {
            const videoId = this.getVideoId(videoPath);
            this.logger.info(`get_captions_thirdparty: video_id: ${videoId} from video_path: ${videoPath}`);

            // const yttApi = new YoutubeTranscript();
            const captions = await YoutubeTranscript.fetchTranscript(videoId)
            //yttApi.fetchTranscript(videoId);

            return captions;  // Returns in dictionary format
        } catch (error: any) {
            this.logger.error(`Error getting captions: ${error}`);
            return null;
        }
    }

    async getCaptionsGoogle(videoPath: string, languageCode: string = "en"): Promise<string | null> {
        // try {
        //     const videoId = this.getVideoId(videoPath);
        //     const credentials = await this.authorization.getCredentials();
        //     //getSessionCredentials();
        //     if (!credentials) {
        //         return "No credentials found";
        //     }

        //     const authedSession = this.authorization.getAuthorizedSession();  // credentials

        //     // 1. Get the list of available caption tracks
        //     const listUrl = `https://www.googleapis.com/youtube/v3/captions?part=snippet&videoId=${videoId}`;
        //     this.logger.info(`get_captions_google: Getting captions from: ${listUrl}`);
        //     if (authedSession){
        //         const response = await authedSession.headers('GET',listUrl);
        //         response.raiseForStatus();
        //         const data: youtube_v3.Schema$CaptionListResponse = response.data;
        //     }
        //     this.logger.info(`get_captions_google: Getting captions ${listUrl} response: ${response.status} ${response.statusText}`);
            
            

        //     const captionTracks = data.items || [];
        //     this.logger.info(`get_captions_google: caption_tracks: ${JSON.stringify(captionTracks)}`);

        //     if (!captionTracks.length) {
        //         this.logger.warn(`get_captions_google: No captions found for video: ${videoId}`);
        //         return "No captions found";
        //     }

        //     // 2. Find the caption track for the desired language (or default to the first one)
        //     let targetTrackId: string | null = null;
        //     for (const track of captionTracks) {
        //         if (track.snippet?.language === languageCode) {
        //             targetTrackId = track.id!;
        //             break;
        //         }
        //     }
        //     this.logger.info(`get_captions_google: target_track_id: ${targetTrackId}`);

        //     if (!targetTrackId) {
        //         this.logger.warn(`No captions found for language code '${languageCode}'. Using the first available track.`);
        //         targetTrackId = captionTracks[0].id!;
        //     }

        //     // 3. Download the caption data
        //     const downloadUrl = `https://www.googleapis.com/youtube/v3/captions/${targetTrackId}?tfmt=srt`;
        //     const downloadResponse = await authedSession.get(downloadUrl, {
        //         responseType: 'text',  // Important for getting text content
        //     });
        //     downloadResponse.raiseForStatus();
        //     this.logger.info(`get_captions_google: download_url ${downloadUrl} response: ${downloadResponse.status} ${downloadResponse.statusText}`);

        //     // 4. Return the caption text
        //     const captionText = downloadResponse.data;
        //     this.logger.info(`get_captions_google: Captions found for video: ${videoId}: ${captionText.substring(0, 200)}...`); // Log first 200 chars
        //     return captionText;

        // } catch (error: any) {
        //     if (error.response) {
        //         if (error.response.status === 403) {
        //             this.logger.error(`Error getting captions: ${error.message}. Check if the video is private or if the API key has the correct permissions.`);
        //             return null;
        //         } else if (error.response.status === 404) {
        //             this.logger.error(`Error getting captions: ${error.message}. No captions found for the video.`);
        //             return null;
        //         } else {
        //             this.logger.error(`Error getting captions: ${error.response.status} - ${error.message}`);
        //             return null;
        //         }
        //     } else {
        //         this.logger.error(`Error getting captions: ${error.message}`);
        //         return null;
        //     }
        // }
        return null
    }
}