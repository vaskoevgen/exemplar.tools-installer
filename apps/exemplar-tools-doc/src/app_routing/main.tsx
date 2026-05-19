import React from 'react';
import { createRoot } from 'react-dom/client';
import { flushSync } from 'react-dom';
import { BrowserRouter } from 'react-router-dom';
import { App } from './App';

const PACT_KEY = "PACT:0cac60:app_routing";
console.debug(PACT_KEY, "main module loaded");

/**
 * Minimal entry point. Creates React root on #root and renders
 * <StrictMode><BrowserRouter><App /></BrowserRouter></StrictMode>.
 *
 * Uses flushSync to ensure synchronous DOM population so that
 * test assertions can verify innerHTML immediately after calling.
 */
export function renderEntryPoint(): void {
  console.debug(PACT_KEY, 'renderEntryPoint called');
  const rootElement = document.getElementById('root');
  if (!rootElement) {
    throw new TypeError('Cannot call createRoot on null — #root element not found in document');
  }
  const root = createRoot(rootElement);

  flushSync(() => {
    root.render(
      React.createElement(
        React.StrictMode,
        null,
        React.createElement(
          BrowserRouter,
          null,
          React.createElement(App),
        ),
      ),
    );
  });
}
