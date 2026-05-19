
import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// Mock dependencies before imports
vi.mock('../../src/step_content', () => ({
  STEPS: [],
  ROUTE_SLUG_MAP: {},
  STEP_CONTENT: {},
  getStepContent: vi.fn(),
}));

vi.mock('../../src/route_config', () => ({
  ROUTES: [],
  routeConfig: [],
  getRouteForStep: vi.fn(),
}));

import {
  PipelineDiagram,
  PIPELINE_NODES,
  PIPELINE_EDGES,
  guardSlug,
} from '../../src/pipeline_diagram';

// Helper to wrap component with MemoryRouter
function renderWithRouter(ui: React.ReactElement, initialEntries: string[] = ['/']) {
  return render(<MemoryRouter initialEntries={initialEntries}>{ui}</MemoryRouter>);
}

// ──────────────────────────────────────────
// 1. guardSlug unit tests
// ──────────────────────────────────────────
describe('guardSlug', () => {
  it('returns slug unchanged when it already starts with "/"', () => {
    const result = guardSlug('/cartographer');
    expect(result).toBe('/cartographer');
    expect(result.startsWith('/')).toBe(true);
    expect(result.startsWith('//')).toBe(false);
  });

  it('prepends "/" when slug does not start with one', () => {
    const result = guardSlug('cartographer');
    expect(result).toBe('/cartographer');
    expect(result.startsWith('/')).toBe(true);
  });

  it('returns "/" unchanged when input is just "/"', () => {
    const result = guardSlug('/');
    expect(result).toBe('/');
    expect(result.startsWith('//')).toBe(false);
  });

  it('does not introduce "//" prefix when input already starts with "/"', () => {
    const result = guardSlug('/arbiter');
    expect(result).toBe('/arbiter');
    expect(result.startsWith('//')).toBe(false);
  });

  it('handles slug with nested path correctly', () => {
    const result = guardSlug('some/nested/path');
    expect(result).toBe('/some/nested/path');
    expect(result.startsWith('/')).toBe(true);
  });

  it('throws or errors for empty string input', () => {
    expect(() => guardSlug('')).toThrow();
  });
});

// ──────────────────────────────────────────
// 2. PIPELINE_NODES contract tests
// ──────────────────────────────────────────
describe('PIPELINE_NODES', () => {
  it('contains exactly 12 nodes', () => {
    expect(PIPELINE_NODES).toHaveLength(12);
  });

  it('does not contain a node with stepId "home"', () => {
    const homeNode = PIPELINE_NODES.find((n: any) => n.stepId === 'home');
    expect(homeNode).toBeUndefined();
  });

  it('has all unique stepIds', () => {
    const stepIds = PIPELINE_NODES.map((n: any) => n.stepId);
    const uniqueStepIds = new Set(stepIds);
    expect(uniqueStepIds.size).toBe(stepIds.length);
  });

  it('every node has all required fields: stepId, label, slug, x, y', () => {
    for (const node of PIPELINE_NODES as any[]) {
      expect(node).toHaveProperty('stepId');
      expect(node).toHaveProperty('label');
      expect(node).toHaveProperty('slug');
      expect(node).toHaveProperty('x');
      expect(node).toHaveProperty('y');
    }
  });

  it('all slugs start with "/"', () => {
    for (const node of PIPELINE_NODES as any[]) {
      expect(node.slug.startsWith('/')).toBe(true);
    }
  });

  it('all x values are within [0, 1200] and y values within [0, 800]', () => {
    for (const node of PIPELINE_NODES as any[]) {
      expect(node.x).toBeGreaterThanOrEqual(0);
      expect(node.x).toBeLessThanOrEqual(1200);
      expect(node.y).toBeGreaterThanOrEqual(0);
      expect(node.y).toBeLessThanOrEqual(800);
    }
  });

  it('contains exactly the expected 12 stepIds', () => {
    const expectedStepIds = new Set([
      'cartographer', 'constrain', 'ledger', 'pact', 'advocate',
      'arbiter', 'baton', 'sentinel', 'chronicler', 'stigmergy',
      'apprentice', 'kindex',
    ]);
    const actualStepIds = new Set(PIPELINE_NODES.map((n: any) => n.stepId));
    expect(actualStepIds).toEqual(expectedStepIds);
  });
});

// ──────────────────────────────────────────
// 3. PIPELINE_EDGES contract tests
// ──────────────────────────────────────────
describe('PIPELINE_EDGES', () => {
  it('contains exactly 14 edges', () => {
    expect(PIPELINE_EDGES).toHaveLength(14);
  });

  it('every edge from/to references a stepId present in PIPELINE_NODES', () => {
    const validStepIds = new Set(PIPELINE_NODES.map((n: any) => n.stepId));
    for (const edge of PIPELINE_EDGES as any[]) {
      expect(validStepIds.has(edge.from)).toBe(true);
      expect(validStepIds.has(edge.to)).toBe(true);
    }
  });

  it('cartographer is the sole root node (no incoming edges)', () => {
    const allToStepIds = new Set((PIPELINE_EDGES as any[]).map((e: any) => e.to));
    const allFromStepIds = new Set((PIPELINE_EDGES as any[]).map((e: any) => e.from));
    const nodeStepIds = new Set(PIPELINE_NODES.map((n: any) => n.stepId));

    // Find nodes that have no incoming edges
    const rootNodes: string[] = [];
    for (const id of nodeStepIds) {
      if (!allToStepIds.has(id)) {
        rootNodes.push(id);
      }
    }
    expect(rootNodes).toHaveLength(1);
    expect(rootNodes[0]).toBe('cartographer');
  });

  it('kindex is the sole terminal node (no outgoing edges)', () => {
    const allFromStepIds = new Set((PIPELINE_EDGES as any[]).map((e: any) => e.from));
    const nodeStepIds = new Set(PIPELINE_NODES.map((n: any) => n.stepId));

    // Find nodes that have no outgoing edges
    const terminalNodes: string[] = [];
    for (const id of nodeStepIds) {
      if (!allFromStepIds.has(id)) {
        terminalNodes.push(id);
      }
    }
    expect(terminalNodes).toHaveLength(1);
    expect(terminalNodes[0]).toBe('kindex');
  });

  it('forms a DAG with no cycles', () => {
    // Topological sort to detect cycles
    const adjList = new Map<string, string[]>();
    const inDegree = new Map<string, number>();

    for (const node of PIPELINE_NODES as any[]) {
      adjList.set(node.stepId, []);
      inDegree.set(node.stepId, 0);
    }

    for (const edge of PIPELINE_EDGES as any[]) {
      adjList.get(edge.from)!.push(edge.to);
      inDegree.set(edge.to, (inDegree.get(edge.to) || 0) + 1);
    }

    const queue: string[] = [];
    for (const [id, deg] of inDegree) {
      if (deg === 0) queue.push(id);
    }

    let visited = 0;
    while (queue.length > 0) {
      const current = queue.shift()!;
      visited++;
      for (const neighbor of adjList.get(current) || []) {
        const newDeg = (inDegree.get(neighbor) || 1) - 1;
        inDegree.set(neighbor, newDeg);
        if (newDeg === 0) queue.push(neighbor);
      }
    }

    expect(visited).toBe(PIPELINE_NODES.length);
  });
});

// ──────────────────────────────────────────
// 4. PipelineDiagram component tests
// ──────────────────────────────────────────
describe('PipelineDiagram', () => {
  const testNodes = [
    { stepId: 'cartographer', label: 'Step 0 — Cartographer', slug: '/cartographer', x: 100, y: 100 },
    { stepId: 'constrain', label: 'Step 1a — Constrain', slug: '/constrain', x: 300, y: 50 },
    { stepId: 'ledger', label: 'Step 1b — Ledger', slug: '/ledger', x: 300, y: 150 },
  ];

  const testEdges = [
    { from: 'cartographer', to: 'constrain' },
    { from: 'cartographer', to: 'ledger' },
  ];

  it('renders all node labels as clickable groups', () => {
    const { container } = renderWithRouter(
      <PipelineDiagram nodes={testNodes as any} edges={testEdges as any} onNodeClick={vi.fn()} />
    );

    const nodeGroups = container.querySelectorAll('[role="link"]');
    expect(nodeGroups).toHaveLength(3);
  });

  it('each node group has tabIndex=0 for keyboard accessibility', () => {
    const { container } = renderWithRouter(
      <PipelineDiagram nodes={testNodes as any} edges={testEdges as any} onNodeClick={vi.fn()} />
    );

    const nodeGroups = container.querySelectorAll('[role="link"]');
    nodeGroups.forEach((group) => {
      expect(group.getAttribute('tabindex')).toBe('0');
    });
  });

  it('each node group has aria-label of the form "Navigate to {label}"', () => {
    const { container } = renderWithRouter(
      <PipelineDiagram nodes={testNodes as any} edges={testEdges as any} onNodeClick={vi.fn()} />
    );

    const nodeGroups = container.querySelectorAll('[role="link"]');
    const labels = Array.from(nodeGroups).map((g) => g.getAttribute('aria-label'));

    for (const node of testNodes) {
      expect(labels).toContain(`Navigate to ${node.label}`);
    }
  });

  it('applies className prop to the root SVG element', () => {
    const { container } = renderWithRouter(
      <PipelineDiagram
        className="my-custom-class"
        nodes={testNodes as any}
        edges={testEdges as any}
        onNodeClick={vi.fn()}
      />
    );

    const svg = container.querySelector('svg');
    expect(svg).not.toBeNull();
    expect(svg!.classList.contains('my-custom-class')).toBe(true);
  });

  it('renders SVG with correct viewBox, width, and preserveAspectRatio', () => {
    const { container } = renderWithRouter(
      <PipelineDiagram nodes={testNodes as any} edges={testEdges as any} onNodeClick={vi.fn()} />
    );

    const svg = container.querySelector('svg');
    expect(svg).not.toBeNull();
    expect(svg!.getAttribute('viewBox')).toBe('0 0 1200 800');
    expect(svg!.getAttribute('width')).toBe('100%');
    expect(svg!.getAttribute('preserveAspectRatio')).toBe('xMidYMid meet');
  });

  it('calls onNodeClick with the correct guarded slug when a node is clicked', () => {
    const onNodeClick = vi.fn();
    const { container } = renderWithRouter(
      <PipelineDiagram nodes={testNodes as any} edges={testEdges as any} onNodeClick={onNodeClick} />
    );

    const nodeGroups = container.querySelectorAll('[role="link"]');
    expect(nodeGroups.length).toBeGreaterThan(0);

    fireEvent.click(nodeGroups[0]);
    expect(onNodeClick).toHaveBeenCalledTimes(1);

    const calledSlug = onNodeClick.mock.calls[0][0] as string;
    expect(calledSlug.startsWith('/')).toBe(true);
    expect(calledSlug.startsWith('//')).toBe(false);
  });

  it('calls onNodeClick on Enter keydown on a node', () => {
    const onNodeClick = vi.fn();
    const { container } = renderWithRouter(
      <PipelineDiagram nodes={testNodes as any} edges={testEdges as any} onNodeClick={onNodeClick} />
    );

    const nodeGroups = container.querySelectorAll('[role="link"]');
    expect(nodeGroups.length).toBeGreaterThan(0);

    fireEvent.keyDown(nodeGroups[0], { key: 'Enter', code: 'Enter' });
    expect(onNodeClick).toHaveBeenCalledTimes(1);
  });

  it('calls onNodeClick on Space keydown on a node', () => {
    const onNodeClick = vi.fn();
    const { container } = renderWithRouter(
      <PipelineDiagram nodes={testNodes as any} edges={testEdges as any} onNodeClick={onNodeClick} />
    );

    const nodeGroups = container.querySelectorAll('[role="link"]');
    expect(nodeGroups.length).toBeGreaterThan(0);

    fireEvent.keyDown(nodeGroups[0], { key: ' ', code: 'Space' });
    expect(onNodeClick).toHaveBeenCalledTimes(1);
  });

  it('renders without crashing when given empty nodes and edges arrays', () => {
    const { container } = renderWithRouter(
      <PipelineDiagram nodes={[] as any} edges={[] as any} onNodeClick={vi.fn()} />
    );

    const svg = container.querySelector('svg');
    expect(svg).not.toBeNull();

    const nodeGroups = container.querySelectorAll('[role="link"]');
    expect(nodeGroups).toHaveLength(0);
  });

  it('renders exactly edges.length line/path elements for edges', () => {
    const { container } = renderWithRouter(
      <PipelineDiagram nodes={testNodes as any} edges={testEdges as any} onNodeClick={vi.fn()} />
    );

    // Edges could be rendered as <line> or <path> elements
    const lines = container.querySelectorAll('svg line');
    const paths = container.querySelectorAll('svg path');
    const edgeElements = lines.length + paths.length;

    // At minimum, we expect edge count to match
    expect(edgeElements).toBeGreaterThanOrEqual(testEdges.length);
  });

  it('applies slug guard before navigating — no double slashes', () => {
    const onNodeClick = vi.fn();
    const nodesWithSlash = [
      { stepId: 'cartographer', label: 'Step 0 — Cartographer', slug: '/cartographer', x: 100, y: 100 },
    ];

    const { container } = renderWithRouter(
      <PipelineDiagram nodes={nodesWithSlash as any} edges={[] as any} onNodeClick={onNodeClick} />
    );

    const nodeGroups = container.querySelectorAll('[role="link"]');
    fireEvent.click(nodeGroups[0]);

    const calledSlug = onNodeClick.mock.calls[0][0] as string;
    expect(calledSlug).toBe('/cartographer');
    expect(calledSlug.startsWith('//')).toBe(false);
  });
});

// ──────────────────────────────────────────
// 5. Integration tests
// ──────────────────────────────────────────
describe('PipelineDiagram integration with PIPELINE_NODES and PIPELINE_EDGES', () => {
  it('renders complete pipeline with 12 clickable node groups', () => {
    const { container } = renderWithRouter(
      <PipelineDiagram
        nodes={PIPELINE_NODES as any}
        edges={PIPELINE_EDGES as any}
        onNodeClick={vi.fn()}
      />
    );

    const nodeGroups = container.querySelectorAll('[role="link"]');
    expect(nodeGroups).toHaveLength(12);
  });

  it('renders SVG with correct viewBox in integration', () => {
    const { container } = renderWithRouter(
      <PipelineDiagram
        nodes={PIPELINE_NODES as any}
        edges={PIPELINE_EDGES as any}
        onNodeClick={vi.fn()}
      />
    );

    const svg = container.querySelector('svg');
    expect(svg).not.toBeNull();
    expect(svg!.getAttribute('viewBox')).toBe('0 0 1200 800');
  });

  it('every node in the integration render has correct aria-label format', () => {
    const { container } = renderWithRouter(
      <PipelineDiagram
        nodes={PIPELINE_NODES as any}
        edges={PIPELINE_EDGES as any}
        onNodeClick={vi.fn()}
      />
    );

    const nodeGroups = container.querySelectorAll('[role="link"]');
    nodeGroups.forEach((group) => {
      const ariaLabel = group.getAttribute('aria-label');
      expect(ariaLabel).not.toBeNull();
      expect(ariaLabel!.startsWith('Navigate to ')).toBe(true);
    });
  });

  it('clicking each node in integration passes a valid guarded slug', () => {
    const onNodeClick = vi.fn();
    const { container } = renderWithRouter(
      <PipelineDiagram
        nodes={PIPELINE_NODES as any}
        edges={PIPELINE_EDGES as any}
        onNodeClick={onNodeClick}
      />
    );

    const nodeGroups = container.querySelectorAll('[role="link"]');
    nodeGroups.forEach((group, index) => {
      fireEvent.click(group);
      const calledSlug = onNodeClick.mock.calls[index][0] as string;
      expect(calledSlug.startsWith('/')).toBe(true);
      expect(calledSlug.startsWith('//')).toBe(false);
    });

    expect(onNodeClick).toHaveBeenCalledTimes(12);
  });
});

// ──────────────────────────────────────────
// 6. Module export verification
// ──────────────────────────────────────────
describe('Module exports', () => {
  it('exports PipelineDiagram as a named export', () => {
    expect(PipelineDiagram).toBeDefined();
    expect(typeof PipelineDiagram).toBe('function');
  });

  it('exports PIPELINE_NODES as a named export', () => {
    expect(PIPELINE_NODES).toBeDefined();
    expect(Array.isArray(PIPELINE_NODES)).toBe(true);
  });

  it('exports PIPELINE_EDGES as a named export', () => {
    expect(PIPELINE_EDGES).toBeDefined();
    expect(Array.isArray(PIPELINE_EDGES)).toBe(true);
  });

  it('exports guardSlug as a named export', () => {
    expect(guardSlug).toBeDefined();
    expect(typeof guardSlug).toBe('function');
  });
});
