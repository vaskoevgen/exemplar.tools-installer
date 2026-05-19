const PACT_KEY = "PACT:d97abb:project_scaffold";
console.debug(PACT_KEY, "tailwind.config loaded");

const config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
};

export default config;
