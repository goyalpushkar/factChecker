// src/ai/flows/summarize-text.ts
'use server';

/**
 * @fileOverview Text summarization AI agent.
 *
 * - summarizeText - A function that handles the text summarization process.
 * - SummarizeTextInput - The input type for the summarizeText function.
 * - SummarizeTextOutput - The return type for the summarizeText function.
 */

import {ai} from '@/ai/ai-instance';
import {z} from 'genkit';

const SummarizeTextInputSchema = z.object({
  text: z.string().describe('The text to summarize.'),
  length: z.string().describe('The desired length of the summary (short, medium, long).'),
});
export type SummarizeTextInput = z.infer<typeof SummarizeTextInputSchema>;

const SummarizeTextOutputSchema = z.object({
  summary: z.string().describe('The summarized text.'),
});
export type SummarizeTextOutput = z.infer<typeof SummarizeTextOutputSchema>;

export async function summarizeText(input: SummarizeTextInput): Promise<SummarizeTextOutput> {
  return summarizeTextFlow(input);
}

const prompt = ai.definePrompt({
  name: 'summarizeTextPrompt',
  input: {
    schema: z.object({
      text: z.string().describe('The text to summarize.'),
      length: z.string().describe('The desired length of the summary (short, medium, long).'),
    }),
  },
  output: {
    schema: z.object({
      summary: z.string().describe('The summarized text.'),
    }),
  },
  prompt: `You are a professional summarizer. Please summarize the following text to the length specified.

Text: {{{text}}}

Length: {{{length}}}`,
});

const summarizeTextFlow = ai.defineFlow<
  typeof SummarizeTextInputSchema,
  typeof SummarizeTextOutputSchema
>({
  name: 'summarizeTextFlow',
  inputSchema: SummarizeTextInputSchema,
  outputSchema: SummarizeTextOutputSchema,
},
async input => {
  const {output} = await prompt(input);
  return output!;
});
