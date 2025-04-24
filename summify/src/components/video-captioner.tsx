'use client';

import {useState} from 'react';
import {getVideoCaptions} from '@/ai/flows/get-video-captions';
import {Button} from '@/components/ui/button';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Input} from '@/components/ui/input';
import {Label} from '@/components/ui/label';
import {Textarea} from '@/components/ui/textarea';

function VideoCaptioner() {
  const [videoUrl, setVideoUrl] = useState('');
  const [captions, setCaptions] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleGetCaptions = async () => {
    setIsLoading(true);
    try {
      const result = await getVideoCaptions({videoUrl});
      setCaptions(result.captions);
    } catch (error) {
      console.error('Failed to get captions:', error);
      setCaptions('An error occurred while getting captions.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-3xl bg-card shadow-md rounded-lg mt-4">
      <CardHeader>
        <CardTitle className="text-2xl font-semibold tracking-tight">Video Captioner</CardTitle>
        <CardDescription>Enter a video URL to generate captions</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-2">
          <Label htmlFor="videoUrl">Video URL</Label>
          <Input
            id="videoUrl"
            value={videoUrl}
            onChange={e => setVideoUrl(e.target.value)}
            placeholder="Enter video URL"
            className="bg-input border rounded-md focus:ring-accent focus:border-accent"
          />
        </div>
        <Button
          onClick={handleGetCaptions}
          disabled={isLoading || !videoUrl}
          className="bg-primary text-primary-foreground rounded-md hover:bg-primary/80 focus:ring-accent focus:border-accent"
        >
          {isLoading ? 'Generating Captions...' : 'Get Captions'}
        </Button>
        {captions && (
          <div className="grid gap-2 mt-4">
            <Label htmlFor="captions">Captions</Label>
            <Textarea
              id="captions"
              value={captions}
              readOnly
              className="bg-muted border rounded-md"
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default VideoCaptioner;

