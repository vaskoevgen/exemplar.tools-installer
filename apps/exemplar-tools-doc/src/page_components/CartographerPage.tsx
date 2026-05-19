import React from 'react';
import { CodeBlock, CalloutBox } from 'shared_components';

const PACT_KEY = "PACT:8e0afe:page_components";

export const CartographerPage: React.FC = () => {
  console.debug(PACT_KEY, "CartographerPage render");
  return (
    <div className="page cartographer-page">
      <h1>Cartographer</h1>
      <section>
        <h2>Overview</h2>
        <p>
          Cartographer scans your project and builds a dependency graph of all modules,
          services, and their interconnections.
        </p>
        <CodeBlock language="bash" code="exemplar cartographer scan --root ." title="Scan project" />
        <CalloutBox type="tip" title="Tip">
          Run Cartographer at the repo root to capture all workspace packages.
        </CalloutBox>
        <CalloutBox type="warning" title="Warning">
          Large monorepos may require the --parallel flag to avoid timeouts.
        </CalloutBox>
        <CalloutBox type="gotcha" title="Gotcha">
          Symlinked directories are not followed by default. Use --follow-symlinks to include them.
        </CalloutBox>
      </section>
    </div>
  );
};

export default CartographerPage;
