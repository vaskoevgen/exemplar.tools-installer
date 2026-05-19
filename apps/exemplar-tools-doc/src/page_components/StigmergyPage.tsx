import React from 'react';
import { CodeBlock, CalloutBox } from 'shared_components';

const PACT_KEY = "PACT:8e0afe:page_components";

export const StigmergyPage: React.FC = () => {
  console.debug(PACT_KEY, "StigmergyPage render");
  return (
    <div className="page stigmergy-page">
      <h1>Stigmergy</h1>
      <section>
        <h2>Overview</h2>
        <p>
          Stigmergy enables indirect coordination between pipeline stages through
          shared environmental markers. Stages leave traces that subsequent stages can read.
        </p>
        <CodeBlock language="bash" code="exemplar stigmergy mark --key deploy-ready --value true" title="Set marker" />
        <CalloutBox type="tip" title="Tip">
          Markers are scoped to the current pipeline run by default.
        </CalloutBox>
        <CalloutBox type="warning" title="Warning">
          Expired markers are garbage-collected after 24 hours. Adjust TTL with --ttl.
        </CalloutBox>
      </section>
    </div>
  );
};

export default StigmergyPage;
