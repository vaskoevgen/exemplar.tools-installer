const PACT_KEY = "PACT:0cac60:app_routing";
console.debug(PACT_KEY, "index loaded");

export { PageComponentKey, ROUTE_MANIFEST, getRouteManifest } from './routes';
export type { RouteEntry, RouteManifest, RoutePath, RouteLabel } from './routes';
export { App, App as default, PAGE_COMPONENTS, buildPageComponentMap } from './App';
export type { PageComponentMap, AppProps, ReactComponentType } from './App';
export { renderEntryPoint } from './main';
export { TypeScriptCompileError, NoMatchingRoute, ModuleNotFoundError } from './errors';
