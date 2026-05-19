import React from 'react';
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

export type PageComponentMapType = Record<string, React.ComponentType>;

export const pageComponentMap: PageComponentMapType = {
  home: HomePage,
  cartographer: CartographerPage,
  constrain: ConstrainPage,
  ledger: LedgerPage,
  pact: PactPage,
  advocate: AdvocatePage,
  arbiter: ArbiterPage,
  baton: BatonPage,
  sentinel: SentinelPage,
  chronicler: ChroniclerPage,
  stigmergy: StigmergyPage,
  apprentice: ApprenticePage,
  kindex: KindexPage,
};

export function getPageComponentMap(): PageComponentMapType {
  console.debug(PACT_KEY, "getPageComponentMap called");
  return pageComponentMap;
}
