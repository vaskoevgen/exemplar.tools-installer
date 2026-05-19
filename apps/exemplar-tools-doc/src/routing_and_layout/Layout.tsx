import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';

const PACT_KEY = "PACT:728331:routing_and_layout";

export function Layout(): React.ReactElement {
  console.debug(PACT_KEY, "Layout render");
  return React.createElement(
    'div',
    { className: 'flex min-h-screen' },
    React.createElement(Sidebar),
    React.createElement(
      'main',
      { className: 'flex-1 p-8' },
      React.createElement(Outlet)
    )
  );
}
