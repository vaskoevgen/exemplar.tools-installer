import React from 'react';
import { CodeBlock, CalloutBox } from 'shared_components';

const PACT_KEY = "PACT:8e0afe:page_components";

export const AdvocatePage: React.FC = () => {
  console.debug(PACT_KEY, "AdvocatePage render");
  return (
    <div className="page advocate-page">
      <h1>Advocate</h1>
      <section>
        <h2>Overview</h2>
        <p>
          Advocate generates and manages test suites that advocate for correct behavior.
          It creates contract tests from pact definitions.
        </p>
        <CodeBlock language="bash" code="exemplar advocate generate --from pacts/" title="Generate tests" />
        <CalloutBox type="tip" title="Tip">
          Point Advocate at your pacts directory to auto-generate contract tests.
        </CalloutBox>
        <CalloutBox type="gotcha" title="Gotcha">
          Advocate overwrites existing test files by default. Use --no-overwrite to preserve manual edits.
        </CalloutBox>
      </section>
    </div>
  );
};

export default AdvocatePage;
