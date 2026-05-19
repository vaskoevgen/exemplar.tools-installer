const PACT_KEY = "PACT:c210a0:shared_components";

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class ClipboardUnavailableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ClipboardUnavailableError';
  }
}
