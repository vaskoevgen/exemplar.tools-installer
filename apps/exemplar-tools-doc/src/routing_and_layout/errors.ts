const PACT_KEY = "PACT:728331:routing_and_layout";

export class ModuleNotFoundError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ModuleNotFoundError';
    console.debug(PACT_KEY, "ModuleNotFoundError", { message });
  }
}
