const PACT_KEY = "PACT:3b9bc2:shared_ui";

import React from 'react';
import type { VersionBadgeProps } from './types';

export function VersionBadge(props: VersionBadgeProps): React.ReactElement {
  const { componentName, version } = props;

  return React.createElement(
    'span',
    {
      className: 'inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800',
      'aria-label': `${componentName} version ${version}`,
    },
    React.createElement('span', null, componentName),
    React.createElement('span', { className: 'text-blue-600' }, version)
  );
}
