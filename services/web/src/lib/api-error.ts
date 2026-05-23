export function apiMessage(
  reason: unknown,
  fallback = "The operation failed.",
) {
  if (typeof reason === "object" && reason && "data" in reason) {
    const data = (
      reason as { data?: { detail?: string | Array<{ msg?: string }> } }
    ).data;
    if (typeof data?.detail === "string") return data.detail;
    if (Array.isArray(data?.detail) && data.detail[0]?.msg)
      return data.detail[0].msg;
  }
  return fallback;
}
