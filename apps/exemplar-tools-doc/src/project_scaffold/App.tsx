const PACT_KEY = "PACT:d97abb:project_scaffold";

import React from 'react';
import { BrowserRouter } from 'react-router-dom';

export function App(): React.ReactElement {
  return (
    <BrowserRouter>
      <div id="app-shell"></div>
    </BrowserRouter>
  );
}
