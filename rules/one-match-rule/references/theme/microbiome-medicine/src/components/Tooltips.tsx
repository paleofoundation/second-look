"use client";
import { useEffect } from "react";

// Reproduces the original theme's hover tooltips (citations, glossary terms, author
// bios). Triggers carry class "rgbc-tooltip" + title=".wiki-xxx"/".author-bio-x"; the
// matching tooltip element is ".tooltip.xxx" (hidden by default).
// Hover-intent: a grace delay on leave + the tooltip stays open while hovered, so you
// can move onto the card and click links inside it (e.g. "Read More").
export function Tooltips() {
  useEffect(() => {
    const triggers = Array.from(document.querySelectorAll<HTMLElement>('.rgbc-tooltip[title^="."]'));
    let active: HTMLElement | null = null;
    let hideTimer: ReturnType<typeof setTimeout> | null = null;
    const cleanups: Array<() => void> = [];
    const wired = new Set<HTMLElement>();

    const cancelHide = () => { if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; } };
    const hideNow = () => { if (active) { active.style.display = "none"; active = null; } };
    const scheduleHide = () => { cancelHide(); hideTimer = setTimeout(hideNow, 320); };

    for (const tr of triggers) {
      const sel = tr.getAttribute("title") || "";
      tr.removeAttribute("title"); // suppress the native browser tooltip
      tr.style.cursor = "pointer"; // the original theme's cursor (NOT the "help" question mark)
      const cls = sel.replace(/^\./, "");
      const show = () => {
        let tip: HTMLElement | null = null;
        try {
          tip = (tr.parentElement?.querySelector(`.tooltip.${CSS.escape(cls)}`) ||
            document.querySelector(`.tooltip.${CSS.escape(cls)}`)) as HTMLElement | null;
        } catch { tip = null; }
        if (!tip) return;
        cancelHide();
        if (active && active !== tip) hideNow();
        const r = tr.getBoundingClientRect();
        Object.assign(tip.style, {
          display: "block", position: "fixed", zIndex: "1200", maxWidth: "340px",
          boxShadow: "0 10px 28px rgba(0,0,0,.2)", borderRadius: "8px", overflow: "hidden",
        });
        tip.style.left = Math.max(8, Math.min(window.innerWidth - 350, r.left)) + "px";
        tip.style.top = (r.bottom + 8) + "px";
        active = tip;
        // keep the card open while the pointer is over it (so its links stay clickable)
        if (!wired.has(tip)) {
          wired.add(tip);
          const onTipEnter = () => cancelHide();
          const onTipLeave = () => scheduleHide();
          tip.addEventListener("mouseenter", onTipEnter);
          tip.addEventListener("mouseleave", onTipLeave);
          cleanups.push(() => { tip!.removeEventListener("mouseenter", onTipEnter); tip!.removeEventListener("mouseleave", onTipLeave); });
        }
      };
      tr.addEventListener("mouseenter", show);
      tr.addEventListener("mouseleave", scheduleHide);
      cleanups.push(() => { tr.removeEventListener("mouseenter", show); tr.removeEventListener("mouseleave", scheduleHide); });
    }
    const onScroll = () => { cancelHide(); hideNow(); };
    document.addEventListener("scroll", onScroll, true);
    cleanups.push(() => document.removeEventListener("scroll", onScroll, true));
    return () => { cancelHide(); cleanups.forEach((f) => f()); };
  });
  return null;
}
