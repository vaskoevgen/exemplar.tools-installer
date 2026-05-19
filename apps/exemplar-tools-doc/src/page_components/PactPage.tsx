import React from 'react';
import { CodeBlock, CalloutBox } from 'shared_components';

const PACT_KEY = "PACT:8e0afe:page_components";

export const PactPage: React.FC = () => {
  console.debug(PACT_KEY, "PactPage render");
  return (
    <div className="page pact-page">
      <h1>Pact</h1>
      <section>
        <h2>Overview</h2>
        <p>
          Pact defines interface contracts between components. It generates typed stubs
          and verifies implementations against their declared contracts.
        </p>
        <CodeBlock language="bash" code="exemplar pact verify --all" title="Verify all pacts" />
        <CalloutBox type="tip" title="Tip">
          Run pact verify in CI to catch contract violations before merge.
        </CalloutBox>
        <CalloutBox type="warning" title="Warning">
          Breaking a pact contract will fail the build. Use pact migrate to update contracts safely.
        </CalloutBox>
      </section>
    </div>
  );
};

export default PactPage;
