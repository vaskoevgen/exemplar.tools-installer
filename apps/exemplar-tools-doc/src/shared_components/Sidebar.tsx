import React from 'react';

const PACT_KEY = "PACT:c210a0:shared_components";

import { NavLink } from 'react-router-dom';
import type { SidebarProps } from './types';

export function Sidebar(props: SidebarProps): React.ReactElement {
  const { routes, className } = props;

  return (
    <nav className={`flex flex-col gap-1 p-4 ${className ?? ''}`}>
      {routes.map((route) => (
        <NavLink
          key={route.path}
          to={route.path}
          className={({ isActive }) =>
            `block px-3 py-2 rounded text-sm transition-colors ${
              isActive
                ? 'active bg-blue-100 text-blue-800 font-semibold'
                : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
            }`
          }
        >
          {route.label}
        </NavLink>
      ))}
    </nav>
  );
}

export default Sidebar;
