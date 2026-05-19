const PACT_KEY = "PACT:3b9bc2:shared_ui";

export class ClipboardApiUnavailableError extends Error {
  constructor(message: string = 'Clipboard API is not available') {
    super(message);
    this.name = 'ClipboardApiUnavailableError';
  }
}

export class ClipboardWriteError extends Error {
  constructor(message: string = 'Clipboard write failed') {
    super(message);
    this.name = 'ClipboardWriteError';
  }
}

export class InvalidYouTubeUrlError extends Error {
  constructor(message: string = 'Invalid YouTube URL') {
    super(message);
    this.name = 'InvalidYouTubeUrlError';
  }
}
