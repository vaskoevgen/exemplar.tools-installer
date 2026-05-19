const PACT_KEY = "PACT:728331:routing_and_layout";

/**
 * Pure utility function that guarantees a string has exactly one leading slash.
 * Uses the exact ternary from operating procedures:
 * slug.startsWith('/') ? slug : '/' + slug
 */
export function ensureLeadingSlash(slug: string): string {
  console.debug(PACT_KEY, "ensureLeadingSlash", { input: slug });
  return slug.startsWith('/') ? slug : '/' + slug;
}

/**
 * Pure helper function that returns the appropriate Tailwind CSS class string
 * for active or inactive navigation link styling.
 */
export function getNavLinkClassName(isActive: boolean): string {
  console.debug(PACT_KEY, "getNavLinkClassName", { isActive });
  if (isActive) {
    return 'font-bold text-blue-700 bg-blue-50 px-3 py-2 rounded-md block';
  }
  return 'text-gray-600 hover:text-blue-600 px-3 py-2 rounded-md block';
}
