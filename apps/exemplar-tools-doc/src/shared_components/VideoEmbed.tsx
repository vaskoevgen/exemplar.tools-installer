import React from 'react';

const PACT_KEY = "PACT:c210a0:shared_components";

import type { VideoEmbedProps } from './types';
import { ValidationError } from './types';

const YOUTUBE_PATTERNS = [
  // Standard embed URL
  /^https?:\/\/(?:www\.)?youtube(?:-nocookie)?\.com\/embed\/([a-zA-Z0-9_-]{11})/,
  // Standard watch URL
  /^https?:\/\/(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})/,
  // Short URL
  /^https?:\/\/youtu\.be\/([a-zA-Z0-9_-]{11})/,
];

function extractYouTubeId(url: string): string | null {
  for (const pattern of YOUTUBE_PATTERNS) {
    const match = url.match(pattern);
    if (match && match[1]) {
      return match[1];
    }
  }
  return null;
}

export function VideoEmbed(props: VideoEmbedProps): React.ReactElement {
  const { url, title } = props;

  const videoId = extractYouTubeId(url);

  if (!videoId) {
    throw new ValidationError(
      `[${PACT_KEY}] invalid_youtube_url: '${url}' does not match a valid YouTube URL pattern`
    );
  }

  const embedSrc = `https://www.youtube.com/embed/${videoId}`;
  const effectiveTitle = title && title.length > 0 ? title : 'Video';

  return (
    <div className="aspect-video w-full my-4">
      <iframe
        src={embedSrc}
        title={effectiveTitle}
        className="w-full h-full rounded-lg"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
        frameBorder="0"
      />
    </div>
  );
}

export default VideoEmbed;
