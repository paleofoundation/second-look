"use client";
import { useEffect, useState } from "react";

// WP scroll-to-top: fixed bottom-right circle, red progress ring fills with scroll.
export function ScrollToTop() {
  const [visible, setVisible] = useState(false);
  const [offset, setOffset] = useState(150);

  useEffect(() => {
    function onScroll() {
      const max = document.body.clientHeight - window.innerHeight;
      const pct = max > 0 ? (window.pageYOffset / max) * 100 : 0;
      setOffset(150 - 1.5 * Math.round(pct));
      setVisible(window.pageYOffset > 300);
    }
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, []);

  return (
    <div
      className="scroll-to-top js-scroll-to-top"
      style={{ opacity: visible ? 1 : 0, pointerEvents: visible ? "auto" : "none", transition: "opacity .3s" }}
      onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
      aria-label="Scroll to top"
    >
      <svg width="50" height="50" viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M25 1a24 24 0 110 48 24 24 0 010-48"
          fill="none"
          stroke="var(--color-primary)"
          strokeWidth={2}
          style={{ strokeDasharray: "150,150", strokeDashoffset: offset, transition: "stroke-dashoffset .12s linear" }}
        />
        <path stroke="#000" strokeWidth={2} d="M19 28l6-6 6 6" />
      </svg>
    </div>
  );
}
