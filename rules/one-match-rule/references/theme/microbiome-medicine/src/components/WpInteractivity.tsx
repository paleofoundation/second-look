"use client";
import { useEffect } from "react";
import { createSupabaseBrowser } from "@/lib/supabase/client";

// Re-attaches the interactive behaviors the original front.js provided, on top of
// the verbatim WordPress markup: accordions, highlight toggle, sidebar collapse +
// scroll-spy, and the favorite button (wired to Supabase).
export function WpInteractivity({ itemId }: { itemId: number }) {
  useEffect(() => {
    const cleanups: Array<() => void> = [];

    // Accordions (FAQ + research-feed items)
    document.querySelectorAll<HTMLElement>(".accordion__header, .research-feed__header-wrap").forEach((h) => {
      const onClick = () => {
        const item = h.closest(".accordion__item") || h.parentElement;
        const content = item?.querySelector(".accordion__content");
        const active = h.classList.toggle("accordion__header--active");
        item?.classList.toggle("accordion__item--active", active);
        content?.classList.toggle("accordion__content--active", active);
      };
      h.style.cursor = "pointer";
      h.addEventListener("click", onClick);
      cleanups.push(() => h.removeEventListener("click", onClick));
    });

    // Highlight toggle
    const center = document.querySelector(".research-content__center");
    const group = document.querySelector<HTMLElement>(".mbio-switcher-group");
    const toggle = document.querySelector<HTMLInputElement>("#highlight-toggle");
    if (center && group && toggle && center.querySelectorAll("mark").length) {
      group.style.display = "flex";
      let on = true;
      try { const s = localStorage.getItem("showHighlights"); if (s !== null) on = s === "true"; } catch {}
      toggle.checked = on;
      center.classList.toggle("mark-hidden", !on);
      const onChange = () => {
        try { localStorage.setItem("showHighlights", String(toggle.checked)); } catch {}
        center.classList.toggle("mark-hidden", !toggle.checked);
      };
      toggle.addEventListener("change", onChange);
      cleanups.push(() => toggle.removeEventListener("change", onChange));
    }

    // Sidebar collapse buttons
    document.querySelectorAll<HTMLElement>(".js-research-btn").forEach((b) => {
      const onClick = () => b.closest(".js-research-sidebar")?.classList.toggle("collapsed");
      b.addEventListener("click", onClick);
      cleanups.push(() => b.removeEventListener("click", onClick));
    });

    // Sidebar parent expand/collapse (ports front.js gA accordion): toggle `active`
    // on a parent --h2 item and each following --h3 sibling until the next --h2.
    const toggleChildren = (h2: Element, force?: boolean) => {
      for (let n = h2.nextElementSibling; n && !n.classList.contains("post-content__item--h2"); n = n.nextElementSibling) {
        if (force === undefined) n.classList.toggle("active");
        else n.classList.toggle("active", force);
      }
    };
    const hasChildren = (h2: Element) => {
      for (let n = h2.nextElementSibling; n && !n.classList.contains("post-content__item--h2"); n = n.nextElementSibling) {
        if (n.classList.contains("post-content__item--h3")) return true;
      }
      return false;
    };
    const onAccordionClick = (e: Event) => {
      const h2 = (e.target as HTMLElement).closest?.(".post-content__item--h2");
      if (!h2 || h2.classList.contains("sub-items-disabled") || !hasChildren(h2)) return;
      const active = h2.classList.toggle("active");
      toggleChildren(h2, active);
    };
    document.addEventListener("click", onAccordionClick);
    cleanups.push(() => document.removeEventListener("click", onAccordionClick));

    // Subsections stay COLLAPSED on load — they open only when the user clicks the
    // parent section (manual accordion above). No auto-expand on navigation.

    // Sidebar scroll-spy (active link) + smooth-scroll with sticky-header offset
    const links = Array.from(document.querySelectorAll<HTMLAnchorElement>('.post-content__link[href^="#"]'));
    if (links.length) {
      const ids = links.map((l) => l.getAttribute("href")!.slice(1)).filter(Boolean);
      const onScroll = () => {
        let cur = "";
        for (const id of ids) { const el = document.getElementById(id); if (el && el.getBoundingClientRect().top <= 140) cur = id; }
        for (const l of links) {
          l.classList.toggle("post-content__link--active", l.getAttribute("href") === "#" + cur);
        }
      };
      onScroll();
      window.addEventListener("scroll", onScroll, { passive: true });
      cleanups.push(() => window.removeEventListener("scroll", onScroll));

      for (const l of links) {
        const onLinkClick = (e: Event) => {
          const href = l.getAttribute("href");
          if (!href || !href.startsWith("#")) return;
          const target = document.querySelector(href);
          if (!target) return;
          e.preventDefault();
          const header = document.querySelector<HTMLElement>(".header");
          const offset = (header ? header.offsetHeight : 0) + 100;
          const top = (target as HTMLElement).getBoundingClientRect().top + window.scrollY - offset;
          window.scrollTo({ top, behavior: "smooth" });
        };
        l.addEventListener("click", onLinkClick);
        cleanups.push(() => l.removeEventListener("click", onLinkClick));
      }
    }

    // Follow / Favorite button. The captured markup uses one #follow-page-btn,
    // labelled "Follow page" on encyclopedic pages (-> follows table, feeds the
    // dashboard's Followed Pages) and "Favorite study" on research feeds (-> favorites).
    // The original opened a WP-AJAX modal; here it's a direct, persisted toggle.
    const fbtn = document.querySelector<HTMLElement>("#follow-page-btn");
    if (fbtn) {
      const supabase = createSupabaseBrowser();
      const isFavorite = /favorite/i.test(fbtn.textContent || "");
      const table = isFavorite ? "favorites" : "follows";
      const onLabel = isFavorite ? "Favorited" : "Following";
      const offLabel = isFavorite ? "Favorite study" : "Follow page";
      const icon = fbtn.querySelector("svg")?.outerHTML || "";
      let on = false;
      let busy = false;
      const render = () => {
        fbtn.innerHTML = `${icon} ${on ? `✓ ${onLabel}` : offLabel}`;
        fbtn.classList.toggle("is-active", on);
      };
      (async () => {
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) return;
        const { data } = await supabase.from(table).select("id").eq("content_item_id", itemId).maybeSingle();
        on = !!data;
        render();
      })();
      const onClick = async (e: Event) => {
        e.preventDefault();
        e.stopPropagation();
        if (busy) return;
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) { window.location.href = "/login"; return; }
        busy = true;
        if (on) {
          await supabase.from(table).delete().eq("content_item_id", itemId).eq("user_id", user.id);
          on = false;
        } else {
          await supabase.from(table).insert({ content_item_id: itemId, user_id: user.id });
          on = true;
        }
        busy = false;
        render();
      };
      fbtn.addEventListener("click", onClick);
      cleanups.push(() => fbtn.removeEventListener("click", onClick));
    }

    return () => cleanups.forEach((f) => f());
  }, [itemId]);
  return null;
}
