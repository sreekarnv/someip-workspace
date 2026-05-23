export function captureHref(runId: string, captureName: string) {
  return `/api/v1/runs/${encodeURIComponent(runId)}/captures/${encodeURIComponent(captureName)}`;
}
