"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Suspense, useState } from "react";

const navItems = [
  { href: "/", label: "Обзор" },
  { href: "/teams", label: "Команды" },
  { href: "/players", label: "Игроки" },
  { href: "/matches", label: "Матчи" },
] as const;

function AppShellHeader() {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="relative border-b border-line bg-card/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <Link href="/" className="text-lg font-semibold tracking-tight">
          Volleyball Intelligence
        </Link>
        <button
          type="button"
          className="rounded-md border border-line px-3 py-1.5 text-sm sm:hidden"
          aria-expanded={menuOpen}
          aria-controls="main-nav"
          onClick={() => setMenuOpen((open) => !open)}
        >
          Меню
        </button>
        <nav
          id="main-nav"
          className={`${menuOpen ? "flex" : "hidden"} absolute left-0 right-0 top-[4.25rem] z-10 flex-col gap-1 border-b border-line bg-card px-4 py-3 sm:static sm:flex sm:flex-row sm:border-0 sm:bg-transparent sm:p-0`}
          aria-label="Основная навигация"
        >
          {navItems.map((item) => {
            const active =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMenuOpen(false)}
                className={`rounded-md px-3 py-2 text-sm ${
                  active
                    ? "bg-accent/15 text-accent"
                    : "text-muted hover:text-foreground"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Suspense
        fallback={
          <header className="border-b border-line bg-card/80 px-4 py-4 sm:px-6">
            <span className="text-lg font-semibold">Volleyball Intelligence</span>
          </header>
        }
      >
        <AppShellHeader />
      </Suspense>
      <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-6 px-4 py-8 sm:px-6">
        {children}
      </main>
      <footer className="border-t border-line py-6 text-center text-sm text-muted">
        Аналитика любительского волейбола · read-only MVP
      </footer>
    </>
  );
}
