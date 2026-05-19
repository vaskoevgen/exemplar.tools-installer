import React from 'react';
import { CodeBlock, CalloutBox } from 'shared_components';

const PACT_KEY = "PACT:8e0afe:page_components";

export const ApprenticePage: React.FC = () => {
  console.debug(PACT_KEY, "ApprenticePage render");
  return (
    <div className="page apprentice-page">
      <h1>Apprentice</h1>
      <section>
        <h2>Overview</h2>
        <p>
          Apprentice learns from your pipeline patterns and suggests optimizations.
          It analyzes historical data to recommend improvements.
        </p>
        <CodeBlock language="bash" code="exemplar apprentice analyze --days 30" title="Analyze patterns" />
        <CalloutBox type="tip" title="Tip">
          Run Apprentice weekly to surface new optimization opportunities.
        </CalloutBox>
        <CalloutBox type="gotcha" title="Gotcha">
          Apprentice requires at least 7 days of pipeline history to produce meaningful suggestions.
        </CalloutBox>
      </section>
    </div>
  );
};

export default ApprenticePage;
