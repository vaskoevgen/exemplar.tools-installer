import React from 'react';
import { PageComponentKey } from 'app_routing';
import { HomePage } from './HomePage';
import { CartographerPage } from './CartographerPage';
import { ConstrainPage } from './ConstrainPage';
import { LedgerPage } from './LedgerPage';
import { PactPage } from './PactPage';
import { AdvocatePage } from './AdvocatePage';
import { ArbiterPage } from './ArbiterPage';
import { BatonPage } from './BatonPage';
import { SentinelPage } from './SentinelPage';
import { ChroniclerPage } from './ChroniclerPage';
import { StigmergyPage } from './StigmergyPage';
import { ApprenticePage } from './ApprenticePage';
import { KindexPage } from './KindexPage';

const PACT_KEY = "PACT:8e0afe:page_components";

export const pageComponentMap: Record<string, React.ComponentType> = {
  [PageComponentKey.Home]: HomePage,
  [PageComponentKey.Cartographer]: CartographerPage,
  [PageComponentKey.Constrain]: ConstrainPage,
  [PageComponentKey.Ledger]: LedgerPage,
  [PageComponentKey.Pact]: PactPage,
  [PageComponentKey.Advocate]: AdvocatePage,
  [PageComponentKey.Arbiter]: ArbiterPage,
  [PageComponentKey.Baton]: BatonPage,
  [PageComponentKey.Sentinel]: SentinelPage,
  [PageComponentKey.Chronicler]: ChroniclerPage,
  [PageComponentKey.Stigmergy]: StigmergyPage,
  [PageComponentKey.Apprentice]: ApprenticePage,
  [PageComponentKey.Kindex]: KindexPage,
};

export function getPageComponentMap(): Record<string, React.ComponentType> {
  console.debug(PACT_KEY, 'getPageComponentMap called');
  return pageComponentMap;
}
