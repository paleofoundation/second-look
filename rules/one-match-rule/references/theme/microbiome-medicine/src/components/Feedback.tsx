"use client";
import { useEffect, useState } from "react";

// Reproduces the theme's "Send feedback" button (originally a plugin). Any
// element with class "js-feedback" opens this modal; submissions POST to /api/feedback.
export function Feedback() {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [email, setEmail] = useState("");
  const [state, setState] = useState<"idle" | "sending" | "done" | "error">("idle");

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      const t = (e.target as HTMLElement)?.closest?.(".js-feedback");
      if (t) {
        e.preventDefault();
        setOpen(true);
        setState("idle");
        setMessage("");
      }
    };
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("click", onClick);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("click", onClick);
      document.removeEventListener("keydown", onKey);
    };
  }, []);

  async function submit() {
    if (message.trim().length < 2) return;
    setState("sending");
    try {
      const r = await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, email, pageUrl: location.href }),
      });
      setState(r.ok ? "done" : "error");
    } catch {
      setState("error");
    }
  }

  if (!open) return null;
  return (
    <div
      onClick={(e) => { if (e.target === e.currentTarget) setOpen(false); }}
      style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,.5)", zIndex: 1100, display: "flex", alignItems: "center", justifyContent: "center", padding: "1rem" }}
    >
      <div style={{ background: "#fff", borderRadius: 12, maxWidth: 460, width: "100%", padding: "1.75rem", position: "relative" }}>
        <button onClick={() => setOpen(false)} aria-label="Close" style={{ position: "absolute", top: 12, right: 14, border: "none", background: "transparent", fontSize: "1.5rem", cursor: "pointer", color: "#888" }}>✕</button>
        <h3 style={{ fontFamily: "var(--font-serif)", color: "#cc3333", fontSize: "1.3rem", marginBottom: ".25rem" }}>Send feedback</h3>
        {state === "done" ? (
          <p style={{ color: "#16a34a", marginTop: "1rem" }}>Thanks — your feedback was sent.</p>
        ) : (
          <>
            <p style={{ color: "#6b7280", fontSize: ".9rem", marginBottom: "1rem" }}>Spotted an error or have a suggestion about this page? Let us know.</p>
            <textarea value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Your feedback…" style={{ width: "100%", minHeight: 120, padding: ".7rem", border: "1px solid #d4d4d8", borderRadius: 8, fontSize: ".95rem", resize: "vertical", boxSizing: "border-box" }} />
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email (optional, if you'd like a reply)" style={{ width: "100%", marginTop: ".6rem", padding: ".6rem .7rem", border: "1px solid #d4d4d8", borderRadius: 8, fontSize: ".9rem", boxSizing: "border-box" }} />
            {state === "error" && <p style={{ color: "#b91c1c", fontSize: ".85rem", marginTop: ".5rem" }}>Something went wrong. Please try again.</p>}
            <button onClick={submit} disabled={state === "sending" || message.trim().length < 2}
              style={{ width: "100%", marginTop: "1rem", padding: ".7rem", background: "#cc3333", color: "#fff", border: "none", borderRadius: 8, fontWeight: 600, cursor: "pointer", opacity: state === "sending" || message.trim().length < 2 ? 0.6 : 1 }}>
              {state === "sending" ? "Sending…" : "Send feedback"}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
