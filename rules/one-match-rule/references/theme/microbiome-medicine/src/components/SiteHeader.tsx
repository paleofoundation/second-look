import Link from "next/link";
import { SECTIONS } from "@/lib/content";

export function SiteHeader() {
  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-6 px-4 py-4">
        <Link href="/" className="flex items-baseline gap-2 shrink-0">
          <span className="font-serif text-xl font-semibold text-[var(--color-primary)]">
            Microbiome
          </span>
          <span className="font-serif text-xl font-semibold text-gray-900">
            Signatures
          </span>
        </Link>
        <nav className="flex items-center gap-x-5 gap-y-1 overflow-x-auto text-sm font-medium text-gray-700">
          {SECTIONS.map((s) => (
            <Link
              key={s.segment}
              href={`/${s.segment}`}
              className="whitespace-nowrap hover:text-[var(--color-primary)]"
            >
              {s.nav}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
