import React from 'react';

const PACT_KEY = "PACT:c210a0:shared_components";

import type { CodeBlockProps } from './types';
import { ValidationError, ClipboardUnavailableError } from './types';

export function CodeBlock(props: CodeBlockProps): React.ReactElement {
  const { code, language, title } = props;

  if (!code || code.length === 0) {
    throw new ValidationError(`[${PACT_KEY}] empty_code_string: code prop must be a non-empty string`);
  }

  const effectiveLanguage = language && language.length > 0 ? language : 'bash';

  const handleCopy = (): void => {
    if (!navigator.clipboard) {
      console.error(`[${PACT_KEY}] clipboard_unavailable: navigator.clipboard is undefined`);
      return;
    }
    navigator.clipboard.writeText(code).catch((err: unknown) => {
      console.error(`[${PACT_KEY}] clipboard write failed`, err);
    });
  };

  return (
    <div className="my-4 rounded-lg overflow-hidden bg-gray-900 text-gray-100">
      {title && title.length > 0 && (
        <div className="px-4 py-2 bg-gray-800 text-sm text-gray-300 border-b border-gray-700">
          {title}
        </div>
      )}
      <div className="relative">
        <pre className={`p-4 overflow-x-auto language-${effectiveLanguage}`}>
          <code className={`language-${effectiveLanguage}`}>{code}</code>
        </pre>
        <button
          type="button"
          onClick={handleCopy}
          className="absolute top-2 right-2 px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-gray-200 rounded"
          aria-label="Copy"
        >
          Copy
        </button>
      </div>
    </div>
  );
}

export default CodeBlock;
