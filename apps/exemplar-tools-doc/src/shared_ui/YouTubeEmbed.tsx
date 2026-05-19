const PACT_KEY = "PACT:3b9bc2:shared_ui";

import React from 'react';
import type { YouTubeEmbedProps } from './types';
import { InvalidYouTubeUrlError } from './errors';

export function extractYouTubeVideoId(url: string): string {
  if (!url || typeof url !== 'string') {
    return '';
  }

  // Try youtube.com/watch?v=ID format
  const watchRegex = /(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?(?:[^&]*&)*v=([a-zA-Z0-9_-]{11})/;
  const watchMatch = url.match(watchRegex);
  if (watchMatch && watchMatch[1]) {
    return watchMatch[1];
  }

  // Try youtu.be/ID format
  const shortRegex = /(?:https?:\/\/)?youtu\.be\/([a-zA-Z0-9_-]{11})/;
  const shortMatch = url.match(shortRegex);
  if (shortMatch && shortMatch[1]) {
    return shortMatch[1];
  }

  return '';
}

export function YouTubeEmbed(props: YouTubeEmbedProps): React.ReactElement {
  const { url, title } = props;
  const videoId = extractYouTubeVideoId(url);
  const iframeTitle = title || 'YouTube video';

  if (!videoId) {
    console.warn(`${PACT_KEY} InvalidYouTubeUrlError: Could not extract video ID from URL: ${url}`);
    return React.createElement(
      'div',
      { className: 'aspect-video flex items-center justify-center bg-gray-100 text-gray-500 rounded' },
      'Invalid YouTube URL'
    );
  }

  const embedSrc = `https://www.youtube.com/embed/${videoId}`;

  return React.createElement(
    'div',
    { className: 'aspect-video w-full' },
    React.createElement('iframe', {
      src: embedSrc,
      title: iframeTitle,
      width: '100%',
      height: '100%',
      frameBorder: '0',
      allow: 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture',
      allowFullScreen: true,
    })
  );
}
