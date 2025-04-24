'use client';

import {useState} from 'react';

import {adjustSummaryLength} from '@/ai/flows/adjust-summary-length';
import {Button} from '@/components/ui/button';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Input} from '@/components/ui/input';
import {Label} from '@/components/ui/label';
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';
import {Textarea} from '@/components/ui/textarea';
import VideoCaptioner from '@/components/video-captioner';

export default function Home() {
  const [text, setText] = useState('');
  const [summary, setSummary] = useState('');
  const [length, setLength] = useState<'short' | 'medium' | 'long'>('medium');
  const [isLoading, setIsLoading] = useState(false);

  const handleSummarize = async () => {
    setIsLoading(true);
    try {
      const result = await adjustSummaryLength({text, length});
      setSummary(result.summary);
    } catch (error) {
      console.error('Failed to summarize text:', error);
      setSummary('An error occurred while summarizing.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-start min-h-screen bg-background p-4">
      <Card className="w-full max-w-3xl bg-card shadow-md rounded-lg">
        <CardHeader>
          <CardTitle className="text-2xl font-semibold tracking-tight">Summify</CardTitle>
          <CardDescription>Enter text to summarize</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2">
            <Label htmlFor="text">Text</Label>
            <Textarea
              id="text"
              value={text}
              onChange={e => setText(e.target.value)}
              placeholder="Enter text to summarize"
              className="bg-input border rounded-md focus:ring-accent focus:border-accent"
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="length">Length</Label>
            <Select value={length} onValueChange={value => setLength(value as 'short' | 'medium' | 'long')}>
              <SelectTrigger className="bg-background border rounded-md focus:ring-accent focus:border-accent">
                <SelectValue placeholder="Select length" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="short">Short</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="long">Long</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button
            onClick={handleSummarize}
            disabled={isLoading || !text}
            className="bg-primary text-primary-foreground rounded-md hover:bg-primary/80 focus:ring-accent focus:border-accent"
          >
            {isLoading ? 'Summarizing...' : 'Summarize'}
          </Button>
          {summary && (
            <div className="grid gap-2 mt-4">
              <Label htmlFor="summary">Summary</Label>
              <Input
                id="summary"
                value={summary}
                readOnly
                className="bg-muted border rounded-md"
              />
            </div>
          )}
        </CardContent>
      </Card>
      <VideoCaptioner/>
    </div>
  );
}
