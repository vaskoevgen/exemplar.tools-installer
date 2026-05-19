const PACT_KEY = "PACT:0cac60:app_routing";

import type React from 'react';

export type ReactComponentType = React.ComponentType<unknown>;

export type RoutePath = string;

export type RouteLabel = string;

export interface AppProps {}

export type PageComponentMap = {
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
};
