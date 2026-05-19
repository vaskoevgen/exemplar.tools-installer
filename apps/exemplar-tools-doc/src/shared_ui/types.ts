const PACT_KEY = "PACT:3b9bc2:shared_ui";

export type CalloutVariant = 'gotcha' | 'warning' | 'tip';

export type OptionalString = string | undefined;

export type CodeBlockProps = {
  code: string;
  description?: OptionalString;
};

export type VersionBadgeProps = {
  componentName: string;
  version: string;
};

export type YouTubeEmbedProps = {
  url: string;
  title?: OptionalString;
};

export type CalloutBoxProps = {
  variant: CalloutVariant;
  text: string;
};

export type CalloutVariantClassMap = Record<CalloutVariant, string>;

export type ClipboardWriteResult = {
  success: boolean;
  error?: string;
};

export type YouTubeUrl = string;
