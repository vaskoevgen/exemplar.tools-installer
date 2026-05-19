const PACT_KEY = "PACT:3b9bc2:shared_ui";

export { CodeBlock } from './CodeBlock';
export { VersionBadge } from './VersionBadge';
export { YouTubeEmbed, extractYouTubeVideoId } from './YouTubeEmbed';
export { CalloutBox } from './CalloutBox';
export { ClipboardApiUnavailableError, ClipboardWriteError, InvalidYouTubeUrlError } from './errors';

export type {
  CalloutVariant,
  CodeBlockProps,
  VersionBadgeProps,
  YouTubeEmbedProps,
  CalloutBoxProps,
  CalloutVariantClassMap,
  ClipboardWriteResult,
  OptionalString,
} from './types';
