import { Suspense } from "react";
import { DashboardView } from "@/components/dashboard/dashboard-view";
import { LoadingBlock } from "@/components/ui/async-state";

export default function HomePage() {
  return (
    <Suspense fallback={<LoadingBlock label="Загрузка…" />}>
      <DashboardView />
    </Suspense>
  );
}
