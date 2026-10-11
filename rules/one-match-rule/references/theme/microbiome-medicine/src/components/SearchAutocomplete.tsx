"use client";
import { useEffect } from "react";

// The captured WordPress search forms (`.js-search-form` — in the header, the
// mega-menu, and the homepage hero) had an inline `oninput="rgbc_ajax.run(...)"`
// that drove a live-autocomplete dropdown. `rgbc_ajax` is a WP plugin global that
// doesn't exist in the rebuild, so every keystroke threw and nothing populated.
// This wires each form to /api/search-suggest and renders the grouped results
// (Conditions first) into that form's `.js-search-result`, matching the original.

type Suggestion = { title: string; href: string; label: string };

const escapeHtml = (s: string): string =>
  s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c] as string));

export function SearchAutocomplete() {
  useEffect(() => {
    const cleanups: Array<() => void> = [];

    document.querySelectorAll<HTMLFormElement>(".js-search-form").forEach((form) => {
      const input = form.querySelector<HTMLInputElement>(".js-search-input");
      const result = form.querySelector<HTMLElement>(".js-search-result");
      if (!input || !result) return;

      // Kill the dead WordPress inline handler (rgbc_ajax is undefined here).
      input.removeAttribute("oninput");
      input.oninput = null;

      let timer: ReturnType<typeof setTimeout> | undefined;
      let seq = 0;

      const render = (items: Suggestion[]) => {
        if (!items.length) {
          result.innerHTML = `<div class="rgbc-search__items"><p class="rgbc-search__not-found">No results found.</p></div>`;
        } else {
          const lis = items
            .map(
              (it) =>
                `<li class="rgbc-search__item"><a class="rgbc-search__link" href="${escapeHtml(it.href)}">` +
                `<span class="search__link-text">${escapeHtml(it.title)}</span>` +
                `<span class="rgbc-search__link-type">${escapeHtml(it.label)}</span></a></li>`
            )
            .join("");
          result.innerHTML = `<ul class="rgbc-search__items">${lis}</ul>`;
        }
        result.style.display = "block";
      };

      const run = async (q: string) => {
        const mine = ++seq;
        try {
          const res = await fetch(`/api/search-suggest?q=${encodeURIComponent(q)}`);
          if (mine !== seq) return; // a newer keystroke superseded this request
          const { items } = (await res.json()) as { items: Suggestion[] };
          render(items || []);
        } catch {
          /* network hiccup — leave the previous dropdown state */
        }
      };

      const onInput = () => {
        const q = input.value.trim();
        if (timer) clearTimeout(timer);
        if (q.length < 2) {
          seq++; // invalidate any in-flight request
          result.innerHTML = "";
          result.style.display = "none";
          return;
        }
        timer = setTimeout(() => run(q), 200);
      };

      const onFocus = () => {
        if (result.innerHTML.trim()) result.style.display = "block";
      };

      input.addEventListener("input", onInput);
      input.addEventListener("focus", onFocus);
      cleanups.push(() => {
        if (timer) clearTimeout(timer);
        input.removeEventListener("input", onInput);
        input.removeEventListener("focus", onFocus);
      });
    });

    // Close any open dropdown when clicking outside its form.
    const onDocClick = (e: MouseEvent) => {
      const t = e.target as Element;
      document.querySelectorAll<HTMLElement>(".js-search-result").forEach((r) => {
        if (!r.closest(".js-search-form")?.contains(t)) r.style.display = "none";
      });
    };
    document.addEventListener("click", onDocClick);
    cleanups.push(() => document.removeEventListener("click", onDocClick));

    return () => cleanups.forEach((fn) => fn());
  }, []);

  return null;
}
