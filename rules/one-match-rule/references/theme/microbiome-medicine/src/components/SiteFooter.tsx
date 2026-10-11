import Link from "next/link";
import { SECTIONS } from "@/lib/content";

export function SiteFooter() {
  return (
    <footer className="mt-16 border-t border-gray-200 bg-gray-50">
      {/* Newsletter CTA — recreated from "Join the Frontlines" */}
      <section className="border-b border-gray-200 bg-[var(--color-primary)]">
        <div className="mx-auto max-w-3xl px-4 py-12 text-center text-white">
          <h2 className="font-serif text-2xl font-semibold text-white">
            Join the Frontlines
          </h2>
          <p className="mx-auto mt-2 max-w-xl text-sm text-white/90">
            Become a Microbiome Insider — get new research signatures and
            evidence updates in your inbox.
          </p>
          <form
            className="mx-auto mt-5 flex max-w-md gap-2"
            data-newsletter
            aria-label="Newsletter signup"
          >
            <input
              type="email"
              required
              placeholder="you@example.com"
              className="min-w-0 flex-1 rounded-md border border-white/30 bg-white/95 px-3 py-2 text-sm text-gray-900 outline-none"
            />
            <button
              type="submit"
              className="rounded-md bg-gray-900 px-4 py-2 text-sm font-semibold text-white hover:bg-black"
            >
              Subscribe
            </button>
          </form>
        </div>
      </section>

      <div className="mx-auto max-w-6xl px-4 py-10">
        <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-gray-600">
          {SECTIONS.map((s) => (
            <Link key={s.segment} href={`/${s.segment}`} className="hover:text-[var(--color-primary)]">
              {s.label}
            </Link>
          ))}
        </div>
        <p className="mt-6 text-xs text-gray-500">
          © {new Date().getFullYear()} Microbiome Signatures. A research-grounded
          reference on the human microbiome.
        </p>
      </div>
    </footer>
  );
}
