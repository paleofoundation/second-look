"use client";
import { useEffect, useState } from "react";

// "Show highlights" toggle (WP mbio-switcher). Only appears if the article has
// <mark> highlights; toggles the "mark-hidden" class on the content; persists choice.
export function Highlights() {
  const [hasMarks, setHasMarks] = useState(false);
  const [on, setOn] = useState(true);

  useEffect(() => {
    const center = document.querySelector(".research-content__center");
    if (!center || center.querySelectorAll("mark").length === 0) return;
    setHasMarks(true);
    let initial = true;
    try {
      const saved = localStorage.getItem("showHighlights");
      if (saved !== null) initial = saved === "true";
    } catch {}
    setOn(initial);
    center.classList.toggle("mark-hidden", !initial);
  }, []);

  function toggle(e: React.ChangeEvent<HTMLInputElement>) {
    const v = e.target.checked;
    setOn(v);
    try { localStorage.setItem("showHighlights", String(v)); } catch {}
    document.querySelector(".research-content__center")?.classList.toggle("mark-hidden", !v);
  }

  if (!hasMarks) return null;
  return (
    <div className="mbio-switcher-group" style={{ display: "flex" }}>
      <label className="mbio-switcher-group__label" htmlFor="highlight-toggle">Show highlights</label>
      <label className="mbio-switcher">
        <input type="checkbox" className="mbio-switcher__checkbox" id="highlight-toggle" checked={on} onChange={toggle} />
        <span className="mbio-switcher__slider"></span>
      </label>
    </div>
  );
}
