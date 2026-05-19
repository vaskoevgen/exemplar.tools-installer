import React from 'react';
import { createBrowserRouter } from 'react-router-dom';
import { ROUTE_ENTRY_LIST } from './routes';
import { Layout } from './Layout';
import { ModuleNotFoundError } from './errors';
import type { RouteEntry } from './types';
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
} from 'page_content';

const PACT_KEY = "PACT:728331:routing_and_layout";

const PAGE_COMPONENT_MAP: Record<string, React.ComponentType> = {
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

export function createAppRouter(): ReturnType<typeof createBrowserRouter> {
  console.debug(PACT_KEY, "createAppRouter", { entryCount: ROUTE_ENTRY_LIST.length });

  const children = ROUTE_ENTRY_LIST.map((entry: RouteEntry) => {
    const Component = PAGE_COMPONENT_MAP[entry.stepId];

    if (!Component) {
      throw new ModuleNotFoundError(`Cannot find module for route entry ${entry.stepId}`);
    }

    if (entry.stepId === 'home') {
      return {
        index: true as const,
        element: React.createElement(Component),
      };
    }

    return {
      path: entry.slug.slice(1),
      element: React.createElement(Component),
    };
  });

  return createBrowserRouter([
    {
      path: '/',
      element: React.createElement(Layout),
      children,
    },
  ]);
}
