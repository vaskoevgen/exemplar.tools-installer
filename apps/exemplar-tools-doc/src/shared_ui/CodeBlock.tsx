const PACT_KEY = "PACT:3b9bc2:shared_ui";

import React, { useState, useCallback } from 'react';
import type { CodeBlockProps } from './types';

export function CodeBlock(props: CodeBlockProps): React.ReactElement {
  const { code, description } = props;
  const [copyState, setCopyState] = useState<'idle' | 'copied' | 'error'>('idle');

  const handleCopy = useCallback(async (): Promise<void> => {
    if (!navigator.clipboard) {
      console.warn(`${PACT_KEY} ClipboardApiUnavailableError: Clipboard API is not available`);
      setCopyState('error');
      setTimeout(() => setCopyState('idle'), 2000);
      return;
    }
    try {
      await navigator.clipboard.writeText(code);
      setCopyState('copied');
      setTimeout(() => setCopyState('idle'), 2000);
    } catch (err: unknown) {
      console.warn(`${PACT_KEY} ClipboardWriteError: Failed to copy to clipboard`, err);
      setCopyState('error');
      setTimeout(() => setCopyState('idle'), 2000);
    }
  }, [code]);

  const buttonLabel = copyState === 'copied' ? 'Copied!' : copyState === 'error' ? 'Failed' : 'Copy';

  const children: React.ReactNode[] = [];

  if (description) {
    children.push(
      React.createElement('p', { key: 'desc', className: 'text-sm text-gray-600 mb-2' }, description)
    );
  }

  children.push(
    React.createElement(
      'div',
      { key: 'code-container', className: 'relative' },
      React.createElement(
        'pre',
        { className: 'bg-gray-900 text-green-400 p-4 rounded overflow-x-auto' },
        React.createElement('code', null, code)
      ),
      React.createElement(
        'button',
        {
          type: 'button',
          className: 'absolute top-2 right-2 px-2 py-1 text-xs bg-gray-700 text-white rounded hover:bg-gray-600',
          onClick: handleCopy,
          'aria-label': 'Copy code to clipboard',
        },
        buttonLabel
      )
    )
  );

  return React.createElement('div', { className: 'my-4' }, ...children);
}
