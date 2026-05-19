const PACT_KEY = "PACT:0cac60:app_routing";

export class TypeScriptCompileError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'TypeScriptCompileError';
    console.debug(PACT_KEY, 'TypeScriptCompileError', message);
  }
}

export class NoMatchingRoute extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'NoMatchingRoute';
    console.debug(PACT_KEY, 'NoMatchingRoute', message);
  }
}

export class ModuleNotFoundError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ModuleNotFoundError';
    console.debug(PACT_KEY, 'ModuleNotFoundError', message);
  }
}
