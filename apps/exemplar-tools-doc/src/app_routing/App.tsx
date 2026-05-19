import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { PageLayout } from 'shared_components';
import {
  HomePage,
  CartographerPage,
  ConstrainPage,
  LedgerPage,
  PactPage,
  AdvocatePage,
  ArbiterPage,
  BatonPage,
  SentinelPage,
  ChroniclerPage,
  StigmergyPage,
  ApprenticePage,
  KindexPage,
} from 'page_components';
import { ROUTE_MANIFEST, PageComponentKey } from './routes';
import type { RouteEntry } from './routes';

const PACT_KEY = "PACT:0cac60:app_routing";
console.debug(PACT_KEY, "App module loaded");

/** Opaque reference to React.ComponentType. */
export type ReactComponentType = React.ComponentType;

/** Props for the App component. Empty — App takes no props. */
export interface AppProps {
  // intentionally empty
}

export interface PageComponentMap {
  Home: ReactComponentType;
  Step0Cartographer: ReactComponentType;
  Step1aConstrain: ReactComponentType;
  Step1bLedger: ReactComponentType;
  Step2aPact: ReactComponentType;
  Step2bAdvocate: ReactComponentType;
  Step3Arbiter: ReactComponentType;
  Step4Baton: ReactComponentType;
  Step5aSentinel: ReactComponentType;
  Step5bChronicler: ReactComponentType;
  Step5cStigmergy: ReactComponentType;
  Step6Apprentice: ReactComponentType;
  Step7Kindex: ReactComponentType;
}

export const PAGE_COMPONENTS: PageComponentMap = {
  Home: HomePage,
  Step0Cartographer: CartographerPage,
  Step1aConstrain: ConstrainPage,
  Step1bLedger: LedgerPage,
  Step2aPact: PactPage,
  Step2bAdvocate: AdvocatePage,
  Step3Arbiter: ArbiterPage,
  Step4Baton: BatonPage,
  Step5aSentinel: SentinelPage,
  Step5bChronicler: ChroniclerPage,
  Step5cStigmergy: StigmergyPage,
  Step6Apprentice: ApprenticePage,
  Step7Kindex: KindexPage,
};

const COMPONENT_KEY_TO_MAP_KEY: Record<PageComponentKey, keyof PageComponentMap> = {
  [PageComponentKey.Home]: 'Home',
  [PageComponentKey.Cartographer]: 'Step0Cartographer',
  [PageComponentKey.Constrain]: 'Step1aConstrain',
  [PageComponentKey.Ledger]: 'Step1bLedger',
  [PageComponentKey.Pact]: 'Step2aPact',
  [PageComponentKey.Advocate]: 'Step2bAdvocate',
  [PageComponentKey.Arbiter]: 'Step3Arbiter',
  [PageComponentKey.Baton]: 'Step4Baton',
  [PageComponentKey.Sentinel]: 'Step5aSentinel',
  [PageComponentKey.Chronicler]: 'Step5bChronicler',
  [PageComponentKey.Stigmergy]: 'Step5cStigmergy',
  [PageComponentKey.Apprentice]: 'Step6Apprentice',
  [PageComponentKey.Kindex]: 'Step7Kindex',
};

export function buildPageComponentMap(): PageComponentMap {
  console.debug(PACT_KEY, 'buildPageComponentMap called');
  return { ...PAGE_COMPONENTS };
}

function resolveComponent(entry: RouteEntry): ReactComponentType {
  const mapKey = COMPONENT_KEY_TO_MAP_KEY[entry.componentKey];
  return PAGE_COMPONENTS[mapKey];
}

/**
 * Root React component. Router-agnostic — expects a router ancestor in tree
 * (BrowserRouter in production, MemoryRouter in tests).
 */
export function App(_props?: AppProps): React.ReactElement {
  console.debug(PACT_KEY, 'App render');
  return React.createElement(
    PageLayout,
    { routes: ROUTE_MANIFEST as unknown as RouteEntry[] },
    React.createElement(
      Routes,
      null,
      ...ROUTE_MANIFEST.map((entry: RouteEntry) => {
        const Component = resolveComponent(entry);
        return React.createElement(Route, {
          key: entry.path,
          path: entry.path,
          element: React.createElement(Component),
        });
      }),
    ),
  );
}

export default App;
