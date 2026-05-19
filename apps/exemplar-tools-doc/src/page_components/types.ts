const PACT_KEY = "PACT:8e0afe:page_components";

import type React from 'react';

/**
 * PageComponentKey enum — string values match the canonical keys from app_routing.
 * The contract tests expect lowercase string values: 'home', 'cartographer', etc.
 */
export enum PageComponentKey {
  Home = 'home',
  Cartographer = 'cartographer',
  Constrain = 'constrain',
  Ledger = 'ledger',
  Pact = 'pact',
  Advocate = 'advocate',
  Arbiter = 'arbiter',
  Baton = 'baton',
  Sentinel = 'sentinel',
  Chronicler = 'chronicler',
  Stigmergy = 'stigmergy',
  Apprentice = 'apprentice',
  Kindex = 'kindex',
}

export type ReactFC = React.FC;
export type ReactComponentType = React.ComponentType;

export interface PageComponentMap {
  [PageComponentKey.Home]: ReactComponentType;
  [PageComponentKey.Cartographer]: ReactComponentType;
  [PageComponentKey.Constrain]: ReactComponentType;
  [PageComponentKey.Ledger]: ReactComponentType;
  [PageComponentKey.Pact]: ReactComponentType;
  [PageComponentKey.Advocate]: ReactComponentType;
  [PageComponentKey.Arbiter]: ReactComponentType;
  [PageComponentKey.Baton]: ReactComponentType;
  [PageComponentKey.Sentinel]: ReactComponentType;
  [PageComponentKey.Chronicler]: ReactComponentType;
  [PageComponentKey.Stigmergy]: ReactComponentType;
  [PageComponentKey.Apprentice]: ReactComponentType;
  [PageComponentKey.Kindex]: ReactComponentType;
}

export interface PageHeadingExpectation {
  componentName: string;
  expectedHeading: string;
  pageKey: PageComponentKey;
}
