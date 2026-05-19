import type { RouteEntry, RouteEntryList, RouteSlugMap, StepId, RouteSlug, StepLabel } from './types';

const PACT_KEY = "PACT:728331:routing_and_layout";

export const ROUTE_ENTRY_LIST: RouteEntryList = [
  { stepId: "home" as StepId, slug: "/" as RouteSlug, label: "Home" as StepLabel },
  { stepId: "cartographer" as StepId, slug: "/cartographer" as RouteSlug, label: "Step 0 \u2014 Cartographer" as StepLabel },
  { stepId: "constrain" as StepId, slug: "/constrain" as RouteSlug, label: "Step 1a \u2014 Constrain" as StepLabel },
  { stepId: "ledger" as StepId, slug: "/ledger" as RouteSlug, label: "Step 1b \u2014 Ledger" as StepLabel },
  { stepId: "pact" as StepId, slug: "/pact" as RouteSlug, label: "Step 2a \u2014 Pact" as StepLabel },
  { stepId: "advocate" as StepId, slug: "/advocate" as RouteSlug, label: "Step 2b \u2014 Advocate" as StepLabel },
  { stepId: "arbiter" as StepId, slug: "/arbiter" as RouteSlug, label: "Step 3 \u2014 Arbiter" as StepLabel },
  { stepId: "baton" as StepId, slug: "/baton" as RouteSlug, label: "Step 4 \u2014 Baton" as StepLabel },
  { stepId: "sentinel" as StepId, slug: "/sentinel" as RouteSlug, label: "Step 5a \u2014 Sentinel" as StepLabel },
  { stepId: "chronicler" as StepId, slug: "/chronicler" as RouteSlug, label: "Step 5b \u2014 Chronicler" as StepLabel },
  { stepId: "stigmergy" as StepId, slug: "/stigmergy" as RouteSlug, label: "Step 5c \u2014 Stigmergy" as StepLabel },
  { stepId: "apprentice" as StepId, slug: "/apprentice" as RouteSlug, label: "Step 6 \u2014 Apprentice" as StepLabel },
  { stepId: "kindex" as StepId, slug: "/kindex" as RouteSlug, label: "Step 7 \u2014 Kindex" as StepLabel },
];

export const ROUTE_SLUG_MAP: RouteSlugMap = ROUTE_ENTRY_LIST.reduce(
  (acc, entry) => {
    acc[entry.stepId] = entry.slug;
    return acc;
  },
  {} as Record<StepId, RouteSlug>
) as RouteSlugMap;

console.debug(PACT_KEY, "routes initialized", { entryCount: ROUTE_ENTRY_LIST.length });
