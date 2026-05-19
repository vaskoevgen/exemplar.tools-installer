import React from 'react';
import { CodeBlock, CalloutBox } from 'shared_components';

const PACT_KEY = "PACT:8e0afe:page_components";

export const SentinelPage: React.FC = () => {
  console.debug(PACT_KEY, "SentinelPage render");
  return (
    <div className="page sentinel-page">
      <h1>Sentinel</h1>
      <section>
        <h2>Overview</h2>
        <p>
          Sentinel monitors your pipeline for anomalies and policy violations.
          It provides real-time alerts when thresholds are exceeded.
        </p>
        <CodeBlock language="bash" code="exemplar sentinel watch --config sentinel.yaml" title="Start watching" />
        <CalloutBox type="tip" title="Tip">
          Configure alert thresholds in sentinel.yaml for each monitored metric.
        </CalloutBox>
        <CalloutBox type="warning" title="Warning">
          Sentinel requires a running daemon process. Use exemplar sentinel start to launch it.
        </CalloutBox>
      </section>
    </div>
  );
};

export default SentinelPage;
