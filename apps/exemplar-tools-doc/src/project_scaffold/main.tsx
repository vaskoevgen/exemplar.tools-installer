import React from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import './index.css';

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('missing_root_element: No DOM element with id="root" found in the document.');
}

const root = createRoot(rootElement);
root.render(<App />);
