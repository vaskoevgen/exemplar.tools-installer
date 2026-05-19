import React from 'react';
import { CodeBlock, CalloutBox } from 'shared_components';

const PACT_KEY = "PACT:8e0afe:page_components";

export const LedgerPage: React.FC = () => {
  console.debug(PACT_KEY, "LedgerPage render");
  return (
    <div className="page ledger-page">
      <h1>Ledger</h1>
      <section>
        <h2>Overview</h2>
        <p>
          Ledger tracks every change event across your pipeline, providing a complete
          audit trail of builds, deployments, and configuration changes.
        </p>
        <CodeBlock language="bash" code="exemplar ledger log --format json" title="View ledger" />
        <CalloutBox type="tip" title="Tip">
          Use --format json for machine-readable output.
        </CalloutBox>
        <CalloutBox type="gotcha" title="Gotcha">
          Ledger entries are append-only. You cannot delete or modify past entries.
        </CalloutBox>
      </section>
    </div>
  );
};

export default LedgerPage;
