import React from 'react';

const PACT_KEY = "PACT:c210a0:shared_components";

import type { PageLayoutProps } from './types';
import { Sidebar } from './Sidebar';

export function PageLayout(props: PageLayoutProps): React.ReactElement {
  const { routes, children } = props;

  return (
    <div className="flex flex-col md:flex-row min-h-screen">
      <aside className="w-full md:w-64 md:flex-shrink-0 border-b md:border-b-0 md:border-r border-gray-200 bg-white">
        <Sidebar routes={routes} />
      </aside>
      <main className="flex-1 p-6 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}

export default PageLayout;
