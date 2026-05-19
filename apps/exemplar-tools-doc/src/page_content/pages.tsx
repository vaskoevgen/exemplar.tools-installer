const PACT_KEY = "PACT:fd4843:page_content";

import React from 'react';
import { StepId } from './types';
import { STEP_CONTENT } from './stepContent';
import { StepPage } from './StepPage';

export function CartographerPage(): React.ReactElement {
  console.debug(PACT_KEY, 'CartographerPage:render');
  return React.createElement(StepPage, { content: STEP_CONTENT[StepId.cartographer] });
}

export function ConstrainPage(): React.ReactElement {
  console.debug(PACT_KEY, 'ConstrainPage:render');
  return React.createElement(StepPage, { content: STEP_CONTENT[StepId.constrain] });
}

export function LedgerPage(): React.ReactElement {
  console.debug(PACT_KEY, 'LedgerPage:render');
  return React.createElement(StepPage, { content: STEP_CONTENT[StepId.ledger] });
}

export function PactPage(): React.ReactElement {
  console.debug(PACT_KEY, 'PactPage:render');
  return React.createElement(StepPage, { content: STEP_CONTENT[StepId.pact] });
}

export function AdvocatePage(): React.ReactElement {
  console.debug(PACT_KEY, 'AdvocatePage:render');
  return React.createElement(StepPage, { content: STEP_CONTENT[StepId.advocate] });
}

export function ArbiterPage(): React.ReactElement {
  console.debug(PACT_KEY, 'ArbiterPage:render');
  return React.createElement(StepPage, { content: STEP_CONTENT[StepId.arbiter] });
}

export function BatonPage(): React.ReactElement {
  console.debug(PACT_KEY, 'BatonPage:render');
  return React.createElement(StepPage, { content: STEP_CONTENT[StepId.baton] });
}

export function SentinelPage(): React.ReactElement {
  console.debug(PACT_KEY, 'SentinelPage:render');
  return React.createElement(StepPage, { content: STEP_CONTENT[StepId.sentinel] });
}

export function ChroniclerPage(): React.ReactElement {
  console.debug(PACT_KEY, 'ChroniclerPage:render');
  return React.createElement(StepPage, { content: STEP_CONTENT[StepId.chronicler] });
}

export function StigmergyPage(): React.ReactElement {
  console.debug(PACT_KEY, 'StigmergyPage:render');
  return React.createElement(StepPage, { content: STEP_CONTENT[StepId.stigmergy] });
}

export function ApprenticePage(): React.ReactElement {
  console.debug(PACT_KEY, 'ApprenticePage:render');
  return React.createElement(StepPage, { content: STEP_CONTENT[StepId.apprentice] });
}

export function KindexPage(): React.ReactElement {
  console.debug(PACT_KEY, 'KindexPage:render');
  return React.createElement(StepPage, { content: STEP_CONTENT[StepId.kindex] });
}
