export function formatLimit(days: number): string {
  if (days === 1) return "day"
  if (days === 7) return "week"
  return `${String(days)} days`
}
