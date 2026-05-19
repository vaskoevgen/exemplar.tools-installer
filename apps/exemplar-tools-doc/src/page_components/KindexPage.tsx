import React from 'react';
import { CodeBlock, CalloutBox } from 'shared_components';

const PACT_KEY = "PACT:8e0afe:page_components";

export const KindexPage: React.FC = () => {
  console.debug(PACT_KEY, "KindexPage render");
  return (
    <div className="page kindex-page">
      <h1>Kindex</h1>
      <section>
        <h2>Overview</h2>
        <p>
          Kindex builds and maintains a searchable knowledge index of your entire
          pipeline configuration, history, and documentation.
        </p>
        <CodeBlock language="bash" code="exemplar kindex build --source ." title="Build index" />
        <CalloutBox type="tip" title="Tip">
          Rebuild the index after major configuration changes for accurate search results.
        </CalloutBox>
        <CalloutBox type="warning" title="Warning">
          The index can grow large for projects with extensive history. Use --prune to limit scope.
        </CalloutBox>
      </section>
    </div>
  );
};

export default KindexPage;
