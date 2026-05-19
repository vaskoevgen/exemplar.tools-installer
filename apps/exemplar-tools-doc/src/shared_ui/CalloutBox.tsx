const PACT_KEY = "PACT:3b9bc2:shared_ui";

import React from 'react';
import type { CalloutBoxProps, CalloutVariantClassMap } from './types';

const variantClassMap: CalloutVariantClassMap = {
  gotcha: 'border-l-4 border-red-500 bg-red-50 text-red-900 p-4 rounded',
  warning: 'border-l-4 border-yellow-500 bg-yellow-50 text-yellow-900 p-4 rounded',
  tip: 'border-l-4 border-green-500 bg-green-50 text-green-900 p-4 rounded',
};

export function CalloutBox(props: CalloutBoxProps): React.ReactElement {
  const { variant, text } = props;
  const classes = variantClassMap[variant] || variantClassMap.tip;

  return React.createElement(
    'aside',
    {
      className: classes,
      role: 'alert',
    },
    React.createElement('p', null, text)
  );
}
