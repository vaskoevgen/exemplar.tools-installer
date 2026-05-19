import React from 'react';

const PACT_KEY = "PACT:c210a0:shared_components";

import type { VersionBadgeProps } from './types';
import { ValidationError } from './types';

export function VersionBadge(props: VersionBadgeProps): React.ReactElement {
  const { version, label } = props;

  if (!version || version.length === 0) {
    throw new ValidationError(`[${PACT_KEY}] empty_version: version prop must be a non-empty string`);
  }

  return (
    <span className="inline-flex items-center rounded-full bg-blue-100 text-blue-800 px-3 py-1 text-sm font-medium">
      {label && label.length > 0 && (
        <span className="mr-1">{label}</span>
      )}
      {version}
    </span>
  );
}

export default VersionBadge;
