import React from 'react';
import { createRoot } from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { createAppRouter } from 'routing_and_layout';
import './index.css';

const rootEl = document.getElementById('root');
if (!rootEl) throw new Error('missing_root_element: no #root in DOM');

const router = createAppRouter();
createRoot(rootEl).render(React.createElement(RouterProvider, { router }));
