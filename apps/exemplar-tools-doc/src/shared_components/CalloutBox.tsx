import React from 'react';

const PACT_KEY = "PACT:c210a0:shared_components";

import type { CalloutBoxProps, CalloutType } from './types';
import { CALLOUT_TYPES } from './types';

const styleMap: Record<CalloutType, { border: string; bg: string; icon: string }> = {
  gotcha: {
    border: 'border-red-500',
    bg: 'bg-red-50',
    icon: '⛔',
  },
  warning: {
    border: 'border-amber-500',
    bg: 'bg-amber-50',
    icon: '⚠️',
  },
  tip: {
    border: 'border-green-500',
    bg: 'bg-green-50',
    icon: '💡',
  },
};

export function CalloutBox(props: CalloutBoxProps): React.ReactElement {
  const { type, title, children } = props;

  if (!CALLOUT_TYPES.includes(type as CalloutType)) {
    throw new Error(`[${PACT_KEY}] invalid_callout_type: '${type}' is not one of gotcha, warning, tip`);
  }

  const styles = styleMap[type];

  return (
    <div className={`border-l-4 ${styles.border} ${styles.bg} p-4 my-4 rounded`} role="note">
      <div className="flex items-start gap-2">
        <span className="text-xl" aria-hidden="true">{styles.icon}</span>
        <div className="flex-1">
          {title && title.length > 0 && (
            <h4 className="font-bold mb-1">{title}</h4>
          )}
          <div>{children}</div>
        </div>
      </div>
    </div>
  );
}

export default CalloutBox;
