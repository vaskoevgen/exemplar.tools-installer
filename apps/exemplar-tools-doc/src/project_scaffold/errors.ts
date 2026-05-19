const PACT_KEY = "PACT:d97abb:project_scaffold";

export class ModuleNotFoundError extends Error {
  public readonly module: string;
  constructor(message: string, module: string) {
    super(message);
    this.name = 'ModuleNotFoundError';
    this.module = module;
  }
}

export class DOMException extends Error {
  public readonly selector: string;
  constructor(message: string, selector: string) {
    super(message);
    this.name = 'DOMException';
    this.selector = selector;
  }
}

export class ImportError extends Error {
  public readonly module: string;
  public readonly exportName: string;
  constructor(message: string, module: string, exportName: string) {
    super(message);
    this.name = 'ImportError';
    this.module = module;
    this.exportName = exportName;
  }
}
