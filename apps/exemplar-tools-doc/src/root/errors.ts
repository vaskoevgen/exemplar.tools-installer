const PACT_KEY = "PACT:481349:root";

export class DOMException extends Error {
  public selector: string;
  constructor(message: string, selector: string = '#root') {
    super(message);
    this.name = 'DOMException';
    this.selector = selector;
  }
}

export class ModuleNotFoundError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ModuleNotFoundError';
  }
}

export class ImportError extends Error {
  public module: string;
  public export_name: string;
  constructor(message: string, module: string = '', exportName: string = '') {
    super(message);
    this.name = 'ImportError';
    this.module = module;
    this.export_name = exportName;
  }
}
