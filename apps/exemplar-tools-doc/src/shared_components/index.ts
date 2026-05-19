const PACT_KEY = "PACT:c210a0:shared_components";

// Types re-exported from types.ts
export type {
  CalloutType,
  CalloutBoxProps,
  CodeBlockLanguage,
  CodeBlockProps,
  VersionString,
  VersionBadgeProps,
  YouTubeUrl,
  VideoEmbedProps,
  SidebarProps,
  PageLayoutProps,
  RouteEntry,
  RouteManifest,
} from './types';

export type { PageComponentKey } from './types';

export { CALLOUT_TYPES, ValidationError, ClipboardUnavailableError } from './types';

// Components
export { CalloutBox } from './CalloutBox';
export { CodeBlock } from './CodeBlock';
export { VersionBadge } from './VersionBadge';
export { VideoEmbed } from './VideoEmbed';
export { Sidebar } from './Sidebar';
export { PageLayout } from './PageLayout';
