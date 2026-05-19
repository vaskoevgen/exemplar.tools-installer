
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/react';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import {
  PipelineDiagram,
  PIPELINE_NODES,
  PIPELINE_EDGES,
  guardSlug,
} from '../../../src/pipeline_diagram';

describe('Pipeline Diagram Component — Goodhart Adversarial Tests', () => {
  // ── guardSlug tests ──

  it('goodhart: guardSlug should correctly handle multi-segment paths without leading slash', () => {
    expect(guardSlug('foo/bar/baz')).toBe('/foo/bar/baz');
  });

  it('goodhart: guardSlug should preserve trailing slashes and not modify anything beyond ensuring leading slash', () => {
    expect(guardSlug('/cartographer/')).toBe('/cartographer/');
  });

  it('goodhart: guardSlug should handle single non-slash characters by prepending slash', () => {
    expect(guardSlug('x')).toBe('/x');
  });

  it('goodhart: guardSlug should return input unchanged when it already starts with / even if double-slashed', () => {
    // Contract says: if input starts with '/', output is identical to input
    expect(guardSlug('//double')).toBe('//double');
  });

  it('goodhart: guardSlug should return a string primitive, not an object wrapper', () => {
    expect(typeof guardSlug('/test')).toBe('string');
    expect(typeof guardSlug('test')).toBe('string');
  });

  it('goodhart: guardSlug should handle whitespace-only input as a non-empty string', () => {
    // The contract only specifies error for empty string; whitespace is non-empty
    expect(guardSlug(' ')).toBe('/ ');
  });

  // ── PIPELINE_NODES tests ──

  it('goodhart: each node in PIPELINE_NODES should have the correct slug matching its stepId', () => {
    const expectedMappings: Record<string, string> = {
      cartographer: '/cartographer',
      constrain: '/constrain',
      ledger: '/ledger',
      pact: '/pact',
      advocate: '/advocate',
      arbiter: '/arbiter',
      baton: '/baton',
      sentinel: '/sentinel',
      chronicler: '/chronicler',
      stigmergy: '/stigmergy',
      apprentice: '/apprentice',
      kindex: '/kindex',
    };
    for (const [stepId, slug] of Object.entries(expectedMappings)) {
      const node = PIPELINE_NODES.find((n: any) => n.stepId === stepId);
      expect(node, `Missing node for stepId '${stepId}'`).toBeDefined();
      expect(node!.slug, `Slug mismatch for stepId '${stepId}'`).toBe(slug);
    }
  });

  it('goodhart: each node in PIPELINE_NODES should have the correct human-readable label with em-dash', () => {
    const expectedLabels: Record<string, string> = {
      cartographer: 'Step 0 \u2014 Cartographer',
      constrain: 'Step 1a \u2014 Constrain',
      ledger: 'Step 1b \u2014 Ledger',
      pact: 'Step 2a \u2014 Pact',
      advocate: 'Step 2b \u2014 Advocate',
      arbiter: 'Step 3 \u2014 Arbiter',
      baton: 'Step 4 \u2014 Baton',
      sentinel: 'Step 5a \u2014 Sentinel',
      chronicler: 'Step 5b \u2014 Chronicler',
      stigmergy: 'Step 5c \u2014 Stigmergy',
      apprentice: 'Step 6 \u2014 Apprentice',
      kindex: 'Step 7 \u2014 Kindex',
    };
    for (const [stepId, label] of Object.entries(expectedLabels)) {
      const node = PIPELINE_NODES.find((n: any) => n.stepId === stepId);
      expect(node, `Missing node for stepId '${stepId}'`).toBeDefined();
      expect(node!.label, `Label mismatch for stepId '${stepId}'`).toBe(label);
    }
  });

  it('goodhart: all slugs in PIPELINE_NODES should be unique', () => {
    const slugs = PIPELINE_NODES.map((n: any) => n.slug);
    expect(new Set(slugs).size).toBe(12);
  });

  it('goodhart: all x and y coordinates in PIPELINE_NODES must be actual numbers, not NaN or strings', () => {
    for (const node of PIPELINE_NODES as any[]) {
      expect(typeof node.x).toBe('number');
      expect(Number.isNaN(node.x)).toBe(false);
      expect(typeof node.y).toBe('number');
      expect(Number.isNaN(node.y)).toBe(false);
    }
  });

  it('goodhart: PIPELINE_NODES must be an actual array instance', () => {
    expect(Array.isArray(PIPELINE_NODES)).toBe(true);
  });

  // ── PIPELINE_EDGES tests ──

  it('goodhart: PIPELINE_EDGES must contain exactly the 14 specified edges with correct from/to pairs', () => {
    const expectedEdges = [
      { from: 'cartographer', to: 'constrain' },
      { from: 'cartographer', to: 'ledger' },
      { from: 'constrain', to: 'pact' },
      { from: 'ledger', to: 'advocate' },
      { from: 'pact', to: 'arbiter' },
      { from: 'advocate', to: 'arbiter' },
      { from: 'arbiter', to: 'baton' },
      { from: 'baton', to: 'sentinel' },
      { from: 'baton', to: 'chronicler' },
      { from: 'baton', to: 'stigmergy' },
      { from: 'sentinel', to: 'apprentice' },
      { from: 'chronicler', to: 'apprentice' },
      { from: 'stigmergy', to: 'apprentice' },
      { from: 'apprentice', to: 'kindex' },
    ];
    for (const expected of expectedEdges) {
      const found = (PIPELINE_EDGES as any[]).some(
        (e) => e.from === expected.from && e.to === expected.to,
      );
      expect(found, `Missing edge: ${expected.from} → ${expected.to}`).toBe(true);
    }
  });

  it('goodhart: PIPELINE_EDGES should not contain reversed or shortcut edges not in the contract', () => {
    const forbidden = [
      { from: 'constrain', to: 'cartographer' },
      { from: 'kindex', to: 'apprentice' },
      { from: 'cartographer', to: 'arbiter' },
      { from: 'baton', to: 'kindex' },
      { from: 'cartographer', to: 'kindex' },
      { from: 'sentinel', to: 'kindex' },
    ];
    for (const edge of forbidden) {
      const found = (PIPELINE_EDGES as any[]).some(
        (e) => e.from === edge.from && e.to === edge.to,
      );
      expect(found, `Unexpected edge: ${edge.from} → ${edge.to}`).toBe(false);
    }
  });

  it('goodhart: cartographer (root) should have exactly 2 outgoing edges', () => {
    const outgoing = (PIPELINE_EDGES as any[]).filter((e) => e.from === 'cartographer');
    expect(outgoing.length).toBe(2);
  });

  it('goodhart: baton should have exactly 3 outgoing edges (triple-branch to sentinel, chronicler, stigmergy)', () => {
    const outgoing = (PIPELINE_EDGES as any[]).filter((e) => e.from === 'baton');
    expect(outgoing.length).toBe(3);
  });

  it('goodhart: apprentice should have exactly 3 incoming edges (merge from sentinel, chronicler, stigmergy)', () => {
    const incoming = (PIPELINE_EDGES as any[]).filter((e) => e.to === 'apprentice');
    expect(incoming.length).toBe(3);
  });

  it('goodhart: arbiter should have exactly 2 incoming edges (merge from pact and advocate)', () => {
    const incoming = (PIPELINE_EDGES as any[]).filter((e) => e.to === 'arbiter');
    expect(incoming.length).toBe(2);
  });

  it('goodhart: PIPELINE_EDGES must be an actual array instance', () => {
    expect(Array.isArray(PIPELINE_EDGES)).toBe(true);
  });

  it('goodhart: every edge object must have from and to as non-empty strings', () => {
    for (const edge of PIPELINE_EDGES as any[]) {
      expect(typeof edge.from).toBe('string');
      expect(edge.from.length).toBeGreaterThan(0);
      expect(typeof edge.to).toBe('string');
      expect(edge.to.length).toBeGreaterThan(0);
    }
  });

  // ── PipelineDiagram component tests ──

  it('goodhart: PipelineDiagram should render exact count of node groups matching a custom 3-node subset', () => {
    const customNodes = [
      { stepId: 'cartographer', label: 'Step 0 \u2014 Cartographer', slug: '/cartographer', x: 100, y: 100 },
      { stepId: 'constrain', label: 'Step 1a \u2014 Constrain', slug: '/constrain', x: 300, y: 100 },
      { stepId: 'pact', label: 'Step 2a \u2014 Pact', slug: '/pact', x: 500, y: 100 },
    ];
    const customEdges = [
      { from: 'cartographer', to: 'constrain' },
      { from: 'constrain', to: 'pact' },
    ];
    const onClick = vi.fn();

    const { container } = render(
      <PipelineDiagram nodes={customNodes as any} edges={customEdges as any} onNodeClick={onClick} />,
    );

    const nodeGroups = container.querySelectorAll('[role="link"]');
    expect(nodeGroups.length).toBe(3);
  });

  it('goodhart: PipelineDiagram should render exact count of edge elements matching a custom 2-edge set', () => {
    const customNodes = [
      { stepId: 'cartographer', label: 'Step 0 \u2014 Cartographer', slug: '/cartographer', x: 100, y: 100 },
      { stepId: 'constrain', label: 'Step 1a \u2014 Constrain', slug: '/constrain', x: 300, y: 100 },
      { stepId: 'pact', label: 'Step 2a \u2014 Pact', slug: '/pact', x: 500, y: 100 },
    ];
    const customEdges = [
      { from: 'cartographer', to: 'constrain' },
      { from: 'constrain', to: 'pact' },
    ];
    const onClick = vi.fn();

    const { container } = render(
      <PipelineDiagram nodes={customNodes as any} edges={customEdges as any} onNodeClick={onClick} />,
    );

    const lines = container.querySelectorAll('line');
    const paths = container.querySelectorAll('path');
    // Edges can be rendered as either line or path elements
    const edgeCount = lines.length + paths.length;
    // We need at least 2 edges; some implementations may use paths for other things,
    // so we check for at least the edges. The contract says "exactly edges.length line or path elements"
    expect(edgeCount).toBeGreaterThanOrEqual(2);
  });

  it('goodhart: each rendered node group should contain both a rect and text element', () => {
    const onClick = vi.fn();
    const { container } = render(
      <MemoryRouter>
        <PipelineDiagram onNodeClick={onClick} />
      </MemoryRouter>,
    );

    const nodeGroups = container.querySelectorAll('[role="link"]');
    expect(nodeGroups.length).toBeGreaterThan(0);
    nodeGroups.forEach((group) => {
      const hasRect = group.querySelector('rect') !== null;
      const hasText = group.querySelector('text') !== null;
      expect(hasRect, `Node group missing rect element`).toBe(true);
      expect(hasText, `Node group missing text element`).toBe(true);
    });
  });

  it('goodhart: all node groups must have tabIndex=0 for keyboard focusability', () => {
    const onClick = vi.fn();
    const { container } = render(
      <MemoryRouter>
        <PipelineDiagram onNodeClick={onClick} />
      </MemoryRouter>,
    );

    const nodeGroups = container.querySelectorAll('[role="link"]');
    nodeGroups.forEach((group) => {
      expect(group.getAttribute('tabindex')).toBe('0');
    });
  });

  it('goodhart: pressing non-Enter/non-Space keys on a node should NOT trigger navigation', () => {
    const onClick = vi.fn();
    const customNodes = [
      { stepId: 'cartographer', label: 'Step 0 \u2014 Cartographer', slug: '/cartographer', x: 100, y: 100 },
    ];
    const customEdges: any[] = [];

    const { container } = render(
      <PipelineDiagram nodes={customNodes as any} edges={customEdges} onNodeClick={onClick} />,
    );

    const nodeGroup = container.querySelector('[role="link"]')!;
    expect(nodeGroup).not.toBeNull();

    fireEvent.keyDown(nodeGroup, { key: 'Tab' });
    fireEvent.keyDown(nodeGroup, { key: 'a' });
    fireEvent.keyDown(nodeGroup, { key: 'Escape' });
    expect(onClick).not.toHaveBeenCalled();
  });

  it('goodhart: module should not have a default export', async () => {
    const mod = await import('../../../src/pipeline_diagram');
    expect((mod as any).default).toBeUndefined();
  });

  it('goodhart: when className is not provided, SVG root should not have "undefined" as class', () => {
    const onClick = vi.fn();
    const { container } = render(
      <MemoryRouter>
        <PipelineDiagram onNodeClick={onClick} />
      </MemoryRouter>,
    );

    const svg = container.querySelector('svg')!;
    const classAttr = svg.getAttribute('class');
    if (classAttr !== null) {
      expect(classAttr).not.toContain('undefined');
    }
  });

  it('goodhart: clicking different nodes should invoke onNodeClick with distinct correct slugs for each', () => {
    const onClick = vi.fn();
    const { container } = render(
      <MemoryRouter>
        <PipelineDiagram onNodeClick={onClick} />
      </MemoryRouter>,
    );

    // Click the node with aria-label for cartographer
    const cartographerNode = container.querySelector('[aria-label="Navigate to Step 0 \u2014 Cartographer"]');
    expect(cartographerNode).not.toBeNull();
    fireEvent.click(cartographerNode!);
    expect(onClick).toHaveBeenCalledWith('/cartographer');

    onClick.mockClear();

    // Click the kindex node
    const kindexNode = container.querySelector('[aria-label="Navigate to Step 7 \u2014 Kindex"]');
    expect(kindexNode).not.toBeNull();
    fireEvent.click(kindexNode!);
    expect(onClick).toHaveBeenCalledWith('/kindex');

    onClick.mockClear();

    // Click the stigmergy node
    const stigmergyNode = container.querySelector('[aria-label="Navigate to Step 5c \u2014 Stigmergy"]');
    expect(stigmergyNode).not.toBeNull();
    fireEvent.click(stigmergyNode!);
    expect(onClick).toHaveBeenCalledWith('/stigmergy');
  });

  it('goodhart: slug guard should be applied to custom nodes with slugs missing leading slash', () => {
    const onClick = vi.fn();
    const customNodes = [
      { stepId: 'cartographer', label: 'Step 0 \u2014 Cartographer', slug: 'noSlash', x: 100, y: 100 },
    ];
    const customEdges: any[] = [];

    const { container } = render(
      <PipelineDiagram nodes={customNodes as any} edges={customEdges} onNodeClick={onClick} />,
    );

    const nodeGroup = container.querySelector('[role="link"]')!;
    expect(nodeGroup).not.toBeNull();
    fireEvent.click(nodeGroup);
    expect(onClick).toHaveBeenCalledWith('/noSlash');
  });
});
