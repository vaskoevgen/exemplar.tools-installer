import React from 'react';
import { CodeBlock, CalloutBox } from 'shared_components';

const PACT_KEY = "PACT:8e0afe:page_components";

// Import the pipeline diagram SVG as a Vite static asset URL.
// In test environment, vi.mock replaces this with { default: '/mocked-pipeline-diagram.svg' }.
// At Vite runtime, this resolves to a URL string.
import pipelineDiagramImport from '../assets/pipeline-diagram.svg';

// Vite static asset imports resolve to a string at runtime,
// but vi.mock wraps it as { default: '...' }. We need to handle both.
function resolveSvgUrl(imported: unknown): string {
  if (typeof imported === 'string') {
    return imported;
  }
  if (imported && typeof imported === 'object' && 'default' in imported) {
    const val = (imported as Record<string, unknown>).default;
    if (typeof val === 'string') {
      return val;
    }
  }
  return '';
}

export const HomePage: React.FC = () => {
  console.debug(PACT_KEY, "HomePage render");

  const svgUrl = resolveSvgUrl(pipelineDiagramImport);

  return (
    <div className="page home-page">
      <h1>exemplar.tools</h1>
      <img
        src={svgUrl}
        alt="exemplar.tools pipeline diagram"
      />
      <section>
        <h2>Overview</h2>
        <p>
          exemplar.tools is a CLI suite for orchestrating software delivery pipelines.
          Each tool handles a discrete stage of the pipeline — from project scaffolding
          through deployment and beyond.
        </p>
        <CalloutBox type="tip" title="Getting Started">
          Install the full suite with a single command:
        </CalloutBox>
        <CodeBlock language="bash" code="npm install -g exemplar.tools" title="Install" />
      </section>
    </div>
  );
};

export default HomePage;
