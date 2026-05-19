const PACT_KEY = "PACT:0cac60:app_routing";
console.debug(PACT_KEY, "routes module loaded");

/**
 * Discriminator enum identifying each of the 13 page components.
 * Values are the string names used as componentKey in RouteEntry.
 */
export enum PageComponentKey {
  Home = 'Home',
  Cartographer = 'Cartographer',
  Constrain = 'Constrain',
  Ledger = 'Ledger',
  Pact = 'Pact',
  Advocate = 'Advocate',
  Arbiter = 'Arbiter',
  Baton = 'Baton',
  Sentinel = 'Sentinel',
  Chronicler = 'Chronicler',
  Stigmergy = 'Stigmergy',
  Apprentice = 'Apprentice',
  Kindex = 'Kindex',
}

/** A validated URL path string. */
export type RoutePath = string;

/** A validated non-empty string used as the sidebar display label. */
export type RouteLabel = string;

/** A single route definition. */
export interface RouteEntry {
  readonly path: RoutePath;
  readonly label: RouteLabel;
  readonly componentKey: PageComponentKey;
}

/** Ordered array of all 13 route entries. */
export type RouteManifest = readonly RouteEntry[];

/**
 * The canonical readonly route manifest — single source of truth.
 * Order: Home first, then steps 0 through 7 ascending.
 */
export const ROUTE_MANIFEST: RouteManifest = Object.freeze([
  Object.freeze({ path: '/', label: 'Home', componentKey: PageComponentKey.Home }),
  Object.freeze({ path: '/step-0-cartographer', label: 'Step 0 \u2014 Cartographer', componentKey: PageComponentKey.Cartographer }),
  Object.freeze({ path: '/step-1a-constrain', label: 'Step 1a \u2014 Constrain', componentKey: PageComponentKey.Constrain }),
  Object.freeze({ path: '/step-1b-ledger', label: 'Step 1b \u2014 Ledger', componentKey: PageComponentKey.Ledger }),
  Object.freeze({ path: '/step-2a-pact', label: 'Step 2a \u2014 Pact', componentKey: PageComponentKey.Pact }),
  Object.freeze({ path: '/step-2b-advocate', label: 'Step 2b \u2014 Advocate', componentKey: PageComponentKey.Advocate }),
  Object.freeze({ path: '/step-3-arbiter', label: 'Step 3 \u2014 Arbiter', componentKey: PageComponentKey.Arbiter }),
  Object.freeze({ path: '/step-4-baton', label: 'Step 4 \u2014 Baton', componentKey: PageComponentKey.Baton }),
  Object.freeze({ path: '/step-5a-sentinel', label: 'Step 5a \u2014 Sentinel', componentKey: PageComponentKey.Sentinel }),
  Object.freeze({ path: '/step-5b-chronicler', label: 'Step 5b \u2014 Chronicler', componentKey: PageComponentKey.Chronicler }),
  Object.freeze({ path: '/step-5c-stigmergy', label: 'Step 5c \u2014 Stigmergy', componentKey: PageComponentKey.Stigmergy }),
  Object.freeze({ path: '/step-6-apprentice', label: 'Step 6 \u2014 Apprentice', componentKey: PageComponentKey.Apprentice }),
  Object.freeze({ path: '/step-7-kindex', label: 'Step 7 \u2014 Kindex', componentKey: PageComponentKey.Kindex }),
] as RouteEntry[]);

/**
 * Returns the ROUTE_MANIFEST constant.
 */
export function getRouteManifest(): RouteManifest {
  console.debug(PACT_KEY, 'getRouteManifest called');
  return ROUTE_MANIFEST;
}
