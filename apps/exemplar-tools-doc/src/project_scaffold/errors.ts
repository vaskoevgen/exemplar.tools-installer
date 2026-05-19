const PACT_KEY = "PACT:d97abb:project_scaffold";

export enum ScaffoldError {
  DIRECTORY_NOT_FOUND = 'DIRECTORY_NOT_FOUND',
  FILE_ALREADY_EXISTS = 'FILE_ALREADY_EXISTS',
  WRITE_PERMISSION_DENIED = 'WRITE_PERMISSION_DENIED',
  INVALID_OUTPUT_DIR = 'INVALID_OUTPUT_DIR',
}

export class DIRECTORY_NOT_FOUND extends Error {
  readonly code = ScaffoldError.DIRECTORY_NOT_FOUND;
  readonly path: string;
  constructor(p: string) {
    super(`DIRECTORY_NOT_FOUND: ${p} does not exist`);
    this.name = 'DIRECTORY_NOT_FOUND';
    this.path = p;
  }
}

export class FILE_ALREADY_EXISTS extends Error {
  readonly code = ScaffoldError.FILE_ALREADY_EXISTS;
  readonly existingFiles: string[];
  constructor(existingFiles: string[]) {
    super(`FILE_ALREADY_EXISTS: files already exist: ${JSON.stringify(existingFiles)}`);
    this.name = 'FILE_ALREADY_EXISTS';
    this.existingFiles = existingFiles;
  }
}

export class WRITE_PERMISSION_DENIED extends Error {
  readonly code = ScaffoldError.WRITE_PERMISSION_DENIED;
  readonly path: string;
  constructor(p: string) {
    super(`WRITE_PERMISSION_DENIED: ${p}`);
    this.name = 'WRITE_PERMISSION_DENIED';
    this.path = p;
  }
}

export class INVALID_OUTPUT_DIR extends Error {
  readonly code = ScaffoldError.INVALID_OUTPUT_DIR;
  readonly outputDir: string;
  constructor(outputDir: string) {
    super(`INVALID_OUTPUT_DIR: invalid outputDir: ${JSON.stringify(outputDir)}`);
    this.name = 'INVALID_OUTPUT_DIR';
    this.outputDir = outputDir;
  }
}
