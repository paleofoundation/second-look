"use client";
import { useEffect } from "react";

// The captured header has a <button class="js-header-search"> that the original
// front.js opened a search overlay with. front.js doesn't run here, so wire the
// button to the /search explore page.
export function HeaderSearch() {
  useEffect(() => {
    const btns = Array.from(document.querySelectorAll<HTMLElement>(".js-header-search"));
    if (!btns.length) return;
    const onClick = (e: Event) => {
      e.preventDefault();
      window.location.href = "/search";
    };
    btns.forEach((b) => b.addEventListener("click", onClick));
    return () => btns.forEach((b) => b.removeEventListener("click", onClick));
  }, []);
  return null;
}
