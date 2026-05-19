import React from 'react';
import { useNavigate } from 'react-router-dom';
import type {
  DiagramNode,
  DiagramNodeList,
  PipelineEdge,
  PipelineEdgeList,
  PipelineDiagramProps,
  GuardedSlug,
} from './types';

const PACT_KEY = "PACT:b6e5b9:pipeline_diagram";

// ── RenderWarning ────────────────────────────
export class RenderWarning extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'RenderWarning';
  }
}

// ── guardSlug ────────────────────────────────
export function guardSlug(slug: string): GuardedSlug {
  if (slug === '') {
    throw new Error('Slug must not be empty.');
  }
  return slug.startsWith('/') ? slug : '/' + slug;
}

// ── PIPELINE_NODES ───────────────────────────
export const PIPELINE_NODES: DiagramNodeList = [
  { stepId: 'cartographer', label: 'Step 0 \u2014 Cartographer', slug: '/cartographer', x: 100, y: 400 },
  { stepId: 'constrain',    label: 'Step 1a \u2014 Constrain',   slug: '/constrain',    x: 280, y: 300 },
  { stepId: 'ledger',       label: 'Step 1b \u2014 Ledger',      slug: '/ledger',       x: 280, y: 500 },
  { stepId: 'pact',         label: 'Step 2a \u2014 Pact',        slug: '/pact',         x: 460, y: 300 },
  { stepId: 'advocate',     label: 'Step 2b \u2014 Advocate',    slug: '/advocate',     x: 460, y: 500 },
  { stepId: 'arbiter',      label: 'Step 3 \u2014 Arbiter',      slug: '/arbiter',      x: 600, y: 400 },
  { stepId: 'baton',        label: 'Step 4 \u2014 Baton',        slug: '/baton',        x: 740, y: 400 },
  { stepId: 'sentinel',     label: 'Step 5a \u2014 Sentinel',    slug: '/sentinel',     x: 900, y: 250 },
  { stepId: 'chronicler',   label: 'Step 5b \u2014 Chronicler',  slug: '/chronicler',   x: 900, y: 400 },
  { stepId: 'stigmergy',    label: 'Step 5c \u2014 Stigmergy',   slug: '/stigmergy',    x: 900, y: 550 },
  { stepId: 'apprentice',   label: 'Step 6 \u2014 Apprentice',   slug: '/apprentice',   x: 1050, y: 400 },
  { stepId: 'kindex',       label: 'Step 7 \u2014 Kindex',       slug: '/kindex',       x: 1150, y: 400 },
];

// ── PIPELINE_EDGES ───────────────────────────
export const PIPELINE_EDGES: PipelineEdgeList = [
  { from: 'cartographer', to: 'constrain' },
  { from: 'cartographer', to: 'ledger' },
  { from: 'constrain',    to: 'pact' },
  { from: 'ledger',       to: 'advocate' },
  { from: 'pact',         to: 'arbiter' },
  { from: 'advocate',     to: 'arbiter' },
  { from: 'arbiter',      to: 'baton' },
  { from: 'baton',        to: 'sentinel' },
  { from: 'baton',        to: 'chronicler' },
  { from: 'baton',        to: 'stigmergy' },
  { from: 'sentinel',     to: 'apprentice' },
  { from: 'chronicler',   to: 'apprentice' },
  { from: 'stigmergy',    to: 'apprentice' },
  { from: 'apprentice',   to: 'kindex' },
];

// ── PipelineDiagram Component ────────────────
export function PipelineDiagram(props: PipelineDiagramProps): React.ReactElement {
  const {
    className = '',
    nodes = PIPELINE_NODES,
    edges = PIPELINE_EDGES,
    onNodeClick,
  } = props;

  // Only call useNavigate if we don't have an external handler
  // We always call it (hooks must not be conditional), but guard usage
  let navigate: ((path: string) => void) | undefined;
  try {
    const nav = useNavigate();
    navigate = nav;
  } catch {
    // If no router context and no onNodeClick, we'll handle at click time
    navigate = undefined;
  }

  const handleNodeInteraction = (slug: string) => {
    console.log(`${PACT_KEY} node_click slug=${slug}`);
    const guarded = guardSlug(slug);
    if (onNodeClick) {
      onNodeClick(guarded);
    } else if (navigate) {
      navigate(guarded);
    } else {
      throw new Error('useNavigate() may be used only in the context of a <Router> component.');
    }
  };

  const handleKeyDown = (slug: string, event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleNodeInteraction(slug);
    }
  };

  // Build a lookup map for node positions by stepId
  const nodeMap = new Map<string, DiagramNode>();
  for (const node of nodes) {
    nodeMap.set(node.stepId, node);
  }

  // Box dimensions
  const boxWidth = 140;
  const boxHeight = 40;
  const boxRx = 6;

  return (
    <svg
      className={className || undefined}
      viewBox="0 0 1200 800"
      width="100%"
      preserveAspectRatio="xMidYMid meet"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Render edges */}
      {edges.map((edge, idx) => {
        const fromNode = nodeMap.get(edge.from);
        const toNode = nodeMap.get(edge.to);
        if (!fromNode || !toNode) {
          console.warn(`${PACT_KEY} Edge references unknown stepId; the edge will not be rendered.`);
          return null;
        }
        return (
          <line
            key={`edge-${idx}`}
            x1={fromNode.x}
            y1={fromNode.y}
            x2={toNode.x}
            y2={toNode.y}
            stroke="#94a3b8"
            strokeWidth={2}
            markerEnd="url(#arrowhead)"
          />
        );
      })}

      {/* Arrow marker definition */}
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="7"
          refX="10"
          refY="3.5"
          orient="auto"
        >
          <polygon points="0 0, 10 3.5, 0 7" fill="#94a3b8" />
        </marker>
      </defs>

      {/* Render nodes */}
      {nodes.map((node) => (
        <g
          key={node.stepId}
          role="link"
          tabIndex={0}
          aria-label={`Navigate to ${node.label}`}
          onClick={() => handleNodeInteraction(node.slug)}
          onKeyDown={(e) => handleKeyDown(node.slug, e)}
          style={{ cursor: 'pointer' }}
        >
          <rect
            x={node.x - boxWidth / 2}
            y={node.y - boxHeight / 2}
            width={boxWidth}
            height={boxHeight}
            rx={boxRx}
            fill="#1e293b"
            stroke="#3b82f6"
            strokeWidth={2}
          />
          <text
            x={node.x}
            y={node.y}
            textAnchor="middle"
            dominantBaseline="central"
            fill="#e2e8f0"
            fontSize={11}
            fontFamily="sans-serif"
          >
            {node.label}
          </text>
        </g>
      ))}
    </svg>
  );
}
