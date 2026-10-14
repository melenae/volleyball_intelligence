import type { DataOrigin } from "@/types/api";

export function DemoBadge({ dataOrigin }: { dataOrigin?: DataOrigin }) {
  if (dataOrigin !== "demo") {
    return null;
  }
  return (
    <p
      className="rounded-md border border-accent/40 bg-accent/10 px-3 py-1.5 text-sm text-accent"
      role="status"
    >
      Демонстрационные данные
    </p>
  );
}
