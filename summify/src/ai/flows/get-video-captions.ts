'use server';

/**
 * @fileOverview A video captioning AI agent.
 *
 * - getVideoCaptions - A function that handles the video captioning process.
 * - GetVideoCaptionsInput - The input type for the getVideoCaptions function.
 * - GetVideoCaptionsOutput - The return type for the getVideoCaptions function.
 */

import { CaptionDerivation } from './CaptionDerivation';
import Logger from '@/lib/Logger';
import {ai} from '@/ai/ai-instance';
import {z} from 'genkit';

const GetVideoCaptionsInputSchema = z.object({
  
  videoUrl: z.string().describe('The URL of the video.'),
});
export type GetVideoCaptionsInput = z.infer<typeof GetVideoCaptionsInputSchema>;

const GetVideoCaptionsOutputSchema = z.object({
  captions: z.string().describe('The generated captions for the video.'),
});
export type GetVideoCaptionsOutput = z.infer<typeof GetVideoCaptionsOutputSchema>;

export async function getVideoCaptions(input: GetVideoCaptionsInput): Promise<GetVideoCaptionsOutput> {
  return getVideoCaptionsFlow(input);
}

const prompt = ai.definePrompt({
  name: 'getVideoCaptionsPrompt',
  input: {
    schema: z.object({
      videoUrl: z.string().describe('The URL of the video.'),
    }),
  },
  output: {
    schema: z.object({
      captions: z.string().describe('The generated captions for the video.'),
    }),
  },
  prompt: `You are an expert video caption generator. Please generate captions for the following video.
Video URL: {{{videoUrl}}}`,
});

const getVideoCaptionsFlow = ai.defineFlow<
    typeof GetVideoCaptionsInputSchema,
    typeof GetVideoCaptionsOutputSchema
  >({
      name: 'getVideoCaptionsFlow',
      inputSchema: GetVideoCaptionsInputSchema,
      outputSchema: GetVideoCaptionsOutputSchema,
    },
    async input => {
      const logger = new Logger();
      logger.log(`Input videoUrl: ${input.videoUrl}`);

      let { output } = await prompt(input);
      logger.log(`Initial prompt output: ${JSON.stringify(output)}`);

      if (output){
        if (!output.captions) {
          const CapDeriv = new CaptionDerivation()
          const fallbackCaptions = await CapDeriv.get_captions(input.videoUrl);
          if (fallbackCaptions) {
            output = { captions: fallbackCaptions };
            logger.log(`Fallback captions used: ${fallbackCaptions}`);
          } else {
            logger.log("No fallback captions available.");
          }
        }
        logger.log(`Final captions: ${output.captions}`);
      }
      return output!;
    });
