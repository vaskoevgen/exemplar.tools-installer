const PACT_KEY = "PACT:b6e5b9:pipeline_diagram";

export enum StepId {
  home = 'home',
  cartographer = 'cartographer',
  constrain = 'constrain',
  ledger = 'ledger',
  pact = 'pact',
  advocate = 'advocate',
  arbiter = 'arbiter',
  baton = 'baton',
  sentinel = 'sentinel',
  chronicler = 'chronicler',
  stigmergy = 'stigmergy',
  apprentice = 'apprentice',
  kindex = 'kindex',
}

export enum StepLabel {
  Home = 'Home',
  Step0Cartographer = 'Step 0 \u2014 Cartographer',
  Step1aConstrain = 'Step 1a \u2014 Constrain',
  Step1bLedger = 'Step 1b \u2014 Ledger',
  Step2aPact = 'Step 2a \u2014 Pact',
  Step2bAdvocate = 'Step 2b \u2014 Advocate',
  Step3Arbiter = 'Step 3 \u2014 Arbiter',
  Step4Baton = 'Step 4 \u2014 Baton',
  Step5aSentinel = 'Step 5a \u2014 Sentinel',
  Step5bChronicler = 'Step 5b \u2014 Chronicler',
  Step5cStigmergy = 'Step 5c \u2014 Stigmergy',
  Step6Apprentice = 'Step 6 \u2014 Apprentice',
  Step7Kindex = 'Step 7 \u2014 Kindex',
}

export enum RouteSlug {
  Root = '/',
  Cartographer = '/cartographer',
  Constrain = '/constrain',
  Ledger = '/ledger',
  Pact = '/pact',
  Advocate = '/advocate',
  Arbiter = '/arbiter',
  Baton = '/baton',
  Sentinel = '/sentinel',
  Chronicler = '/chronicler',
  Stigmergy = '/stigmergy',
  Apprentice = '/apprentice',
  Kindex = '/kindex',
}

export interface PipelineNode {
  stepId: string;
  label: string;
  slug: string;
  x: number;
  y: number;
}

export type PipelineNodeList = PipelineNode[];

export interface DiagramNode {
  stepId: string;
  label: string;
  slug: string;
  x: number;
  y: number;
}

export type DiagramNodeList = DiagramNode[];

export interface PipelineEdge {
  from: string;
  to: string;
}

export type PipelineEdgeList = PipelineEdge[];

export type NodeClickHandler = (slug: string) => void;

export type GuardedSlug = string;

export interface PipelineDiagramProps {
  className?: string;
  nodes?: DiagramNodeList;
  edges?: PipelineEdgeList;
  onNodeClick?: NodeClickHandler;
}
