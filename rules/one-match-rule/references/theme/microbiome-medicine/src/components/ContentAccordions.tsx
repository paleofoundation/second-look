"use client";
import { useEffect } from "react";

// Wires the click-to-toggle accordions that live inside rendered content_html
// (research-feed study cards + any .accordion__header blocks) for pages that render
// via ArticleView. Mirrors the accordion behavior in WpInteractivity, but WITHOUT its
// sidebar/highlight/follow logic (ArticleView uses SectionNav + FollowButton already).
// Native <details> accordions are left alone (they toggle without JS).
export function ContentAccordions() {
  useEffect(() => {
    const cleanups: Array<() => void> = [];
    document.querySelectorAll<HTMLElement>(".research-content__center .research-feed__header-wrap, .research-content__center .accordion__header").forEach((h) => {
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
    return () => cleanups.forEach((f) => f());
  });
  return null;
}
