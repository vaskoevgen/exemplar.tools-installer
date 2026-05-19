const PACT_KEY = "PACT:481349:root";

import { createAppRouter } from 'routing_and_layout';
import { mountApp } from 'project_scaffold';

export function initApp(): void {
  console.log(`[${PACT_KEY}] initApp: starting application initialization`);

  // Step 1: Create the app router (wires all 13 page components via routing_and_layout)
  const router = createAppRouter();
  console.log(`[${PACT_KEY}] initApp: createAppRouter completed successfully`);

  // Step 2: Mount the application into the DOM
  mountApp(router);
  console.log(`[${PACT_KEY}] initApp: mountApp completed successfully`);
}
