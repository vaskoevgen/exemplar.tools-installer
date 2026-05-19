import React from 'react';
import { CodeBlock, CalloutBox } from 'shared_components';

const PACT_KEY = "PACT:8e0afe:page_components";

export const ArbiterPage: React.FC = () => {
  console.debug(PACT_KEY, "ArbiterPage render");
  return (
    <div className="page arbiter-page">
      <h1>Arbiter</h1>
      <section>
        <h2>Overview</h2>
        <p>
          Arbiter resolves conflicts between competing constraints and contract
          violations. It provides a resolution workflow for teams.
        </p>
        <CodeBlock language="bash" code="exemplar arbiter resolve --interactive" title="Resolve conflicts" />
        <CalloutBox type="tip" title="Tip">
          Use --interactive mode to step through each conflict one at a time.
        </CalloutBox>
        <CalloutBox type="warning" title="Warning">
          Automatic resolution (--auto) may choose a resolution that does not match your intent. Always review.
        </CalloutBox>
      </section>
    </div>
  );
};

export default ArbiterPage;
