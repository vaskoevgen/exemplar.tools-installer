const PACT_KEY = "PACT:8e0afe:page_components";
console.debug(PACT_KEY, "barrel loading");

export { HomePage } from './HomePage';
export { CartographerPage } from './CartographerPage';
export { ConstrainPage } from './ConstrainPage';
export { LedgerPage } from './LedgerPage';
export { PactPage } from './PactPage';
export { AdvocatePage } from './AdvocatePage';
export { ArbiterPage } from './ArbiterPage';
export { BatonPage } from './BatonPage';
export { SentinelPage } from './SentinelPage';
export { ChroniclerPage } from './ChroniclerPage';
export { StigmergyPage } from './StigmergyPage';
export { ApprenticePage } from './ApprenticePage';
export { KindexPage } from './KindexPage';
export { pageComponentMap, getPageComponentMap } from './getPageComponentMap';
export type { PageComponentMap, PageHeadingExpectation, PageComponentKey } from './types';
