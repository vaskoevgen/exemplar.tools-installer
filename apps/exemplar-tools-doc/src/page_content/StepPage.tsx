const PACT_KEY = "PACT:fd4843:page_content";

import React from 'react';
import { CodeBlock, CalloutBox, YouTubeEmbed, VersionBadge } from 'shared_ui';
import type { StepContent, StepPageProps } from './types';

export function StepPage({ content }: StepPageProps): React.ReactElement {
  if (content === undefined || content === null) {
    throw new TypeError('StepPage requires a valid StepContent prop.');
  }

  console.debug(PACT_KEY, 'StepPage:render', { stepId: content.stepId });

  return React.createElement('div', { className: 'step-page' },
    // h1 with label
    React.createElement('h1', null, content.label),

    // Version badge (conditional)
    content.version && content.version.length > 0
      ? React.createElement(VersionBadge, { componentName: content.label, version: content.version })
      : null,

    // Overview paragraph
    React.createElement('p', { className: 'overview' }, content.overview),

    // Commands section
    content.commands.length > 0
      ? React.createElement('section', { className: 'commands' },
          React.createElement('h2', null, 'Commands'),
          ...content.commands.map((cmd, i) =>
            React.createElement(CodeBlock, {
              key: `cmd-${i}`,
              code: cmd.command,
              description: cmd.description,
            })
          )
        )
      : null,

    // Callouts section
    content.callouts.length > 0
      ? React.createElement('section', { className: 'callouts' },
          React.createElement('h2', null, 'Notes'),
          ...content.callouts.map((callout, i) =>
            React.createElement(CalloutBox, {
              key: `callout-${i}`,
              variant: callout.variant as unknown as string,
              text: callout.text,
            })
          )
        )
      : null,

    // Examples section
    content.examples.length > 0
      ? React.createElement('section', { className: 'examples' },
          React.createElement('h2', null, 'Examples'),
          ...content.examples.map((example, i) =>
            React.createElement(CodeBlock, {
              key: `example-${i}`,
              code: example,
              description: '',
            })
          )
        )
      : null,

    // YouTube embed (conditional)
    content.youtubeUrl && content.youtubeUrl.length > 0
      ? React.createElement(YouTubeEmbed, { url: content.youtubeUrl, title: content.label })
      : null,
  );
}
