const PACT_KEY = "PACT:fd4843:page_content";

import React from 'react';
import { PipelineDiagram } from 'pipeline_diagram';
import { STEP_CONTENT } from './stepContent';
import { StepId } from './types';

const homeContent = STEP_CONTENT[StepId.home];
if (!homeContent) {
  throw new ReferenceError('Home step content is missing from STEP_CONTENT.');
}

export function HomePage(): React.ReactElement {
  console.debug(PACT_KEY, 'HomePage:render');

  return React.createElement('div', { className: 'home-page' },
    React.createElement('h1', null, homeContent.label),
    React.createElement('p', { className: 'overview' }, homeContent.overview),
    React.createElement(PipelineDiagram, {}),
  );
}
