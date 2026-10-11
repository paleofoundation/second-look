"use client";
import { useEffect, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";

// Share button for content-page heroes. Self-installs right after the page's
// follow/favorite button (`.js-follow-button-wrap`) so it clusters with it — on
// condition heroes that's the single center-tags row; on research-feed pages the
// Favorite study button lives in a second center-tags row, so Share follows it
// there rather than sitting up with the category pill. Falls back to the first
// center-tags row when no follow button exists. Lets users share to major platforms.
type Opt = { key: string; label: string; color: string; href?: (u: string, t: string) => string };
const OPTS: Opt[] = [
  { key: "copy", label: "Copy link", color: "#2c7a7b" },
  { key: "email", label: "Email", color: "#6b46c1", href: (u, t) => `mailto:?subject=${encodeURIComponent(t)}&body=${encodeURIComponent(u)}` },
  { key: "facebook", label: "Facebook", color: "#1877f2", href: (u) => `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(u)}` },
  { key: "twitter", label: "X (Twitter)", color: "#000000", href: (u, t) => `https://twitter.com/intent/tweet?url=${encodeURIComponent(u)}&text=${encodeURIComponent(t)}` },
  { key: "linkedin", label: "LinkedIn", color: "#0a66c2", href: (u) => `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(u)}` },
  { key: "reddit", label: "Reddit", color: "#ff4500", href: (u, t) => `https://www.reddit.com/submit?url=${encodeURIComponent(u)}&title=${encodeURIComponent(t)}` },
];

// Brand glyphs in the same style as the author-page social icons (AuthorSocials.tsx):
// monochrome currentColor paths, shown white inside a brand-colored circle.
const ICON: Record<string, ReactNode> = {
  copy: <svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor" aria-hidden="true"><path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z" /></svg>,
  email: <svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor" aria-hidden="true"><path d="M3 4h18c.55 0 1 .45 1 1v14c0 .55-.45 1-1 1H3c-.55 0-1-.45-1-1V5c0-.55.45-1 1-1zm9 8.69l8-5.34V6l-8 5.34L4 6v1.35l8 5.34z" /></svg>,
  facebook: <svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor" aria-hidden="true"><path d="M24 12.07C24 5.4 18.63 0 12 0S0 5.4 0 12.07c0 6.02 4.39 11.01 10.13 11.93v-8.44H7.08v-3.49h3.05V9.41c0-3.02 1.79-4.69 4.53-4.69 1.31 0 2.69.24 2.69.24v2.97h-1.52c-1.49 0-1.96.93-1.96 1.89v2.25h3.33l-.53 3.49h-2.8V24C19.61 23.08 24 18.09 24 12.07z" /></svg>,
  twitter: <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" /></svg>,
  linkedin: <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 110-4.13 2.06 2.06 0 010 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.8 0 0 .77 0 1.73v20.54C0 23.22.8 24 1.77 24h20.45c.98 0 1.78-.78 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z" /></svg>,
  reddit: <svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor" aria-hidden="true"><path d="M24 12a4.28 4.28 0 00-4.28-4.28c-.98 0-1.87.33-2.58.88a10.66 10.66 0 00-5.66-1.79l.96-4.53 3.15.67a1.5 1.5 0 101.5-1.55l-3.54-.75a.37.37 0 00-.44.28l-1.07 5.04a10.7 10.7 0 00-5.75 1.79 4.26 4.26 0 00-2.58-.88A4.28 4.28 0 000 12c0 1.65.94 3.08 2.3 3.79a4.6 4.6 0 00-.05.71c0 3.6 4.19 6.51 9.36 6.51s9.36-2.91 9.36-6.51c0-.24-.02-.48-.05-.71A4.26 4.26 0 0024 12zM6.67 13.53a1.5 1.5 0 113 0 1.5 1.5 0 01-3 0zm8.37 3.96c-1.02 1.02-2.98 1.1-3.55 1.1-.57 0-2.53-.08-3.55-1.1a.39.39 0 01.55-.55c.64.64 2.02.87 3 .87.98 0 2.36-.23 3-.87a.39.39 0 01.55.55zm-.29-2.46a1.5 1.5 0 110-3 1.5 1.5 0 010 3z" /></svg>,
};

export function ShareButton() {
  const [host, setHost] = useState<HTMLElement | null>(null);
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    // Prefer the center-tags row that holds the follow/favorite button, so Share sits
    // right next to it (research-feed pages keep Favorite study in a second row);
    // otherwise fall back to the first center-tags row.
    const wrap = document.querySelector<HTMLElement>(".js-follow-button-wrap");
    const tags = wrap?.closest<HTMLElement>(".research-hero__center-tags") || document.querySelector<HTMLElement>(".research-hero__center-tags");
    if (!tags) return;
    // Safety net: strip any leftover "Research feed" button (also removed server-side).
    document.querySelectorAll<HTMLElement>(".research-hero__center-tags a.research-hero__center-tag").forEach((a) => {
      if (/research\s*feed/i.test(a.textContent || "") || /research-feeds?/.test(a.getAttribute("href") || "")) a.remove();
    });
    if (tags.querySelector(".rgbc-share")) return; // already installed
    const el = document.createElement("div");
    el.className = "rgbc-share";
    el.style.position = "relative";
    // Sit right after the follow/favorite button so Share clusters with it.
    if (wrap && tags.contains(wrap)) wrap.insertAdjacentElement("afterend", el);
    else tags.appendChild(el);
    setHost(el);
    return () => { el.remove(); };
  }, []);

  useEffect(() => {
    if (!open || !host) return;
    const onDoc = (e: MouseEvent) => { if (!host.contains(e.target as Node)) setOpen(false); };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [open, host]);

  if (!host) return null;

  const doShare = (o: Opt) => {
    const url = window.location.href;
    const title = document.title.replace(/\s*[|–-]\s*Microbiome Medicine.*$/i, "");
    if (o.key === "copy") {
      navigator.clipboard?.writeText(url).then(() => { setCopied(true); setTimeout(() => setCopied(false), 1500); });
      return;
    }
    const href = o.href!(url, title);
    if (o.key === "email") window.location.href = href;
    else window.open(href, "_blank", "noopener,noreferrer,width=600,height=540");
    setOpen(false);
  };

  return createPortal(
    <>
      <button
        type="button"
        className="research-hero__center-tag"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="menu"
        aria-expanded={open}
        style={{ cursor: "pointer", border: "none", font: "inherit" }}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <circle cx="18" cy="5" r="3" /><circle cx="6" cy="12" r="3" /><circle cx="18" cy="19" r="3" />
          <line x1="8.6" y1="13.5" x2="15.4" y2="17.5" /><line x1="15.4" y1="6.5" x2="8.6" y2="10.5" />
        </svg>{" "}Share
      </button>
      {open && (
        <div role="menu" style={{ position: "absolute", top: "calc(100% + 8px)", right: 0, zIndex: 60, background: "#fff", borderRadius: 12, boxShadow: "0 18px 50px -10px rgba(0,0,0,.28)", padding: 8, minWidth: 210 }}>
          {OPTS.map((o) => (
            <button
              key={o.key}
              type="button"
              role="menuitem"
              onClick={() => doShare(o)}
              style={{ display: "flex", alignItems: "center", gap: 12, width: "100%", padding: "10px 12px", border: "none", background: "none", cursor: "pointer", borderRadius: 8, font: "inherit", fontSize: 15, color: "#1a202c", textAlign: "left" }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "#f4f1f7")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "none")}
            >
              <span
                ref={(el) => { if (el) { el.style.setProperty("background", o.color, "important"); el.style.setProperty("color", "#fff", "important"); } }}
                style={{ width: 32, height: 32, borderRadius: "50%", flexShrink: 0, display: "inline-flex", alignItems: "center", justifyContent: "center" }}
              >{ICON[o.key]}</span>
              {o.key === "copy" && copied ? "Copied!" : o.label}
            </button>
          ))}
        </div>
      )}
    </>,
    host
  );
}
