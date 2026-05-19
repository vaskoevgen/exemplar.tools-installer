import React from 'react';
import { CodeBlock, CalloutBox } from 'shared_components';

const PACT_KEY = "PACT:8e0afe:page_components";

export const ChroniclerPage: React.FC = () => {
  console.debug(PACT_KEY, "ChroniclerPage render");
  return (
    <div className="page chronicler-page">
      <h1>Chronicler</h1>
      <section>
        <h2>Overview</h2>
        <p>
          Chronicler generates human-readable changelogs and release notes from
          your pipeline history and commit messages.
        </p>
        <CodeBlock language="bash" code="exemplar chronicler generate --since v1.0.0" title="Generate changelog" />
        <CalloutBox type="tip" title="Tip">
          Use conventional commits for best results with Chronicler.
        </CalloutBox>
        <CalloutBox type="gotcha" title="Gotcha">
          Chronicler skips merge commits by default. Use --include-merges to include them.
        </CalloutBox>
      </section>
    </div>
  );
};

export default ChroniclerPage;
