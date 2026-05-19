const PACT_KEY = "PACT:c210a0:shared_components";

import type { PageComponentKey, RouteEntry } from 'app_routing';

export type { PageComponentKey, RouteEntry } from 'app_routing';

export type RouteManifest = RouteEntry[];

export type CalloutType = 'gotcha' | 'warning' | 'tip';

export const CALLOUT_TYPES: readonly CalloutType[] = ['gotcha', 'warning', 'tip'] as const;

export interface CalloutBoxProps {
  type: CalloutType;
  title?: string;
  children: React.ReactNode;
}

export type CodeBlockLanguage = string;

export interface CodeBlockProps {
  code: string;
  language?: string;
  title?: string;
}

export type VersionString = string;

export interface VersionBadgeProps {
  version: string;
  label?: string;
}

export type YouTubeUrl = string;

export interface VideoEmbedProps {
  url: string;
  title?: string;
}

export interface SidebarProps {
  routes: RouteManifest;
  className?: string;
}

export interface PageLayoutProps {
  routes: RouteManifest;
  children: React.ReactNode;
}

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class ClipboardUnavailableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ClipboardUnavailableError';
  }
}
