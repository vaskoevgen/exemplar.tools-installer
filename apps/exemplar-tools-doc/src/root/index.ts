import { getRouteManifest, buildPageComponentMap, App, renderEntryPoint } from 'app_routing';
import { getPageComponentMap } from 'page_components';
import { getProjectManifest, getRequiredDependencies } from 'project_scaffold';
import { CalloutBox, CodeBlock, VersionBadge, VideoEmbed, Sidebar, PageLayout } from 'shared_components';

export interface BijectionResult {
  isValid: boolean;
  missingInMap: string[];
  extraInMap: string[];
  manifestKeys: string[];
  mapKeys: string[];
}

export interface BootstrapConfig {
  targetElementId: string;
  strictMode?: boolean;
}

export interface BootstrapResult {
  routeCount: number;
  pageComponentCount: number;
  allRoutesHaveComponents: boolean;
  targetElementId: string;
}

export function verifyManifestComponentBijection(
  manifest: ReadonlyArray<{ componentKey: string }>,
  map: Record<string, unknown>,
): BijectionResult {
  const manifestKeys = manifest.map((e) => e.componentKey);
  const mapKeys = Object.keys(map);
  const manifestSet = new Set(manifestKeys);
  const mapSet = new Set(mapKeys);
  const missingInMap = manifestKeys.filter((k) => !mapSet.has(k));
  const extraInMap = mapKeys.filter((k) => !manifestSet.has(k));
  return {
    isValid: missingInMap.length === 0 && extraInMap.length === 0,
    missingInMap,
    extraInMap,
    manifestKeys,
    mapKeys,
  };
}

export function bootstrapApp(config: BootstrapConfig): BootstrapResult {
  if (!config.targetElementId || !config.targetElementId.trim()) {
    throw new Error('TARGET_ELEMENT_NOT_FOUND: targetElementId must be non-empty');
  }
  const el = document.getElementById(config.targetElementId);
  if (!el) {
    throw new Error(`TARGET_ELEMENT_NOT_FOUND: no element with id '${config.targetElementId}'`);
  }
  const manifest = getRouteManifest();
  const map = getPageComponentMap();
  const bijection = verifyManifestComponentBijection(
    manifest as ReadonlyArray<{ componentKey: string }>,
    map as Record<string, unknown>,
  );
  if (!bijection.isValid) {
    throw new Error(
      `MANIFEST_COMPONENT_MISMATCH: missing=[${bijection.missingInMap.join(',')}] extra=[${bijection.extraInMap.join(',')}]`,
    );
  }
  try {
    renderEntryPoint();
  } catch (err) {
    throw new Error(`RENDER_FAILURE: ${err instanceof Error ? err.message : String(err)}`);
  }
  return {
    routeCount: manifest.length,
    pageComponentCount: Object.keys(map).length,
    allRoutesHaveComponents: bijection.isValid,
    targetElementId: config.targetElementId,
  };
}

export {
  getRouteManifest,
  buildPageComponentMap,
  getPageComponentMap,
  getProjectManifest,
  getRequiredDependencies,
  App,
  renderEntryPoint,
  CalloutBox,
  CodeBlock,
  VersionBadge,
  VideoEmbed,
  Sidebar,
  PageLayout,
};
