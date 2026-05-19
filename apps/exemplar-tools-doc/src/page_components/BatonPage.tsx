import React from 'react';
import { CodeBlock, CalloutBox } from 'shared_components';

const PACT_KEY = "PACT:8e0afe:page_components";

export const BatonPage: React.FC = () => {
  console.debug(PACT_KEY, "BatonPage render");
  return (
    <div className="page baton-page">
      <h1>Baton</h1>
      <section>
        <h2>Overview</h2>
        <p>
          Baton manages handoffs between pipeline stages. It ensures that artifacts
          and context are passed correctly from one stage to the next.
        </p>
        <CodeBlock language="bash" code="exemplar baton pass --from build --to deploy" title="Pass baton" />
        <CalloutBox type="tip" title="Tip">
          Baton validates artifact checksums during handoff to prevent corruption.
        </CalloutBox>
        <CalloutBox type="gotcha" title="Gotcha">
          If the receiving stage is not ready, Baton will queue the handoff. Use --no-queue to fail fast.
        </CalloutBox>
      </section>
    </div>
  );
};

export default BatonPage;
