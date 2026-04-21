export function getApiBaseUrl(): string {
  // In production behind CloudFront, prefer same-origin `/api/*` by leaving this empty at build time.
  return process.env.NEXT_PUBLIC_API_URL || "";
}

export function buildApiUrl(path: string): string {
  const base = getApiBaseUrl();
  const normalized = path.startsWith("/") ? path : `/${path}`;
  if (!base) {
    return normalized;
  }
  return `${base.replace(/\/$/, "")}${normalized}`;
}
