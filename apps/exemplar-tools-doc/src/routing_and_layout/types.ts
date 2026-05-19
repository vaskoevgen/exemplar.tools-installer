const PACT_KEY = "PACT:728331:routing_and_layout";

export type RouteSlug = "/" | "/cartographer" | "/constrain" | "/ledger" | "/pact" | "/advocate" | "/arbiter" | "/baton" | "/sentinel" | "/chronicler" | "/stigmergy" | "/apprentice" | "/kindex";

export type StepId = "home" | "cartographer" | "constrain" | "ledger" | "pact" | "advocate" | "arbiter" | "baton" | "sentinel" | "chronicler" | "stigmergy" | "apprentice" | "kindex";

export type StepLabel =
  | "Home"
  | "Step 0 \u2014 Cartographer"
  | "Step 1a \u2014 Constrain"
  | "Step 1b \u2014 Ledger"
  | "Step 2a \u2014 Pact"
  | "Step 2b \u2014 Advocate"
  | "Step 3 \u2014 Arbiter"
  | "Step 4 \u2014 Baton"
  | "Step 5a \u2014 Sentinel"
  | "Step 5b \u2014 Chronicler"
  | "Step 5c \u2014 Stigmergy"
  | "Step 6 \u2014 Apprentice"
  | "Step 7 \u2014 Kindex";

export interface RouteEntry {
  stepId: StepId;
  slug: RouteSlug;
  label: StepLabel;
}

export type RouteEntryList = RouteEntry[];

export type RouteSlugMap = Record<StepId, RouteSlug>;

export type ReactNode = React.ReactNode;

export type NavLinkClassName = (args: { isActive: boolean }) => string;

export interface RouterConfig {
  path: string;
  element: ReactNode;
  children: unknown[];
}
