import { HealthStatus } from "@/components/health-status";

export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-8 px-6 py-16">
      <header className="flex flex-col gap-3">
        <p className="text-sm font-medium tracking-wide text-accent">Phase 1</p>
        <h1 className="text-4xl font-semibold tracking-tight">Volleyball Intelligence</h1>
        <p className="max-w-2xl text-lg leading-8 text-muted">
          Локальный каркас аналитической платформы. Демонстрационные данные лиги ещё не
          загружены. Показатели AVL появятся только после отдельного согласования API.
        </p>
      </header>
      <HealthStatus />
    </main>
  );
}
