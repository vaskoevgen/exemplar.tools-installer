import React from 'react';
import { CodeBlock, CalloutBox } from 'shared_components';

const PACT_KEY = "PACT:8e0afe:page_components";

export const ConstrainPage: React.FC = () => {
  console.debug(PACT_KEY, "ConstrainPage render");
  return (
    <div className="page constrain-page">
      <h1>Constrain</h1>
      <section>
        <h2>Overview</h2>
        <p>
          Constrain defines and enforces architectural boundaries within your codebase.
          It ensures that dependency rules are not violated.
        </p>
        <CodeBlock language="bash" code="exemplar constrain check --config constrain.yaml" title="Check constraints" />
        <CalloutBox type="tip" title="Tip">
          Define boundaries in a constrain.yaml file at your project root.
        </CalloutBox>
        <CalloutBox type="warning" title="Warning">
          Circular dependency detection is enabled by default and may flag legitimate patterns.
        </CalloutBox>
      </section>
    </div>
  );
};

export default ConstrainPage;
