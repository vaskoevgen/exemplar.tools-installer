import React from 'react';
import { NavLink } from 'react-router-dom';
import { ROUTE_ENTRY_LIST } from './routes';
import { getNavLinkClassName } from './utils';
import type { RouteEntry } from './types';

const PACT_KEY = "PACT:728331:routing_and_layout";

export function Sidebar(): React.ReactElement {
  console.debug(PACT_KEY, "Sidebar render");
  return React.createElement(
    'nav',
    { className: 'w-64 min-h-screen bg-gray-50 border-r border-gray-200 p-4' },
    ROUTE_ENTRY_LIST.map((entry: RouteEntry) => {
      const isHome = entry.slug === '/';
      const props: Record<string, unknown> = {
        key: entry.stepId,
        to: entry.slug,
        className: ({ isActive }: { isActive: boolean }) => getNavLinkClassName(isActive),
      };
      if (isHome) {
        props['end'] = true;
      }
      return React.createElement(
        NavLink,
        props as unknown as React.ComponentProps<typeof NavLink>,
        entry.label
      );
    })
  );
}
