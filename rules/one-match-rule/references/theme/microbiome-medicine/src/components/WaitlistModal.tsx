"use client";
import { useEffect, useState } from "react";
import { createSupabaseBrowser } from "@/lib/supabase/client";
import { WaitlistForm } from "@/components/WaitlistForm";

// Mounted once in the root layout. Opens on any click of an element marked
// data-open-waitlist or a link to #join-waitlist (the header CTA and the
// research-summary wall both use that). If the visitor is already signed in,
// the trigger sends them to their dashboard instead of the signup form.
export function WaitlistModal() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const supabase = createSupabaseBrowser();
    async function onClick(e: MouseEvent) {
      const el = (e.target as HTMLElement | null)?.closest<HTMLElement>('[data-open-waitlist], a[href="#join-waitlist"]');
      if (!el) return;
      e.preventDefault();
      const { data } = await supabase.auth.getUser();
      if (data.user) {
        window.location.href = "/dashboard";
        return;
      }
      setOpen(true);
    }
    document.addEventListener("click", onClick);
    return () => document.removeEventListener("click", onClick);
  }, []);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    if (open) {
      document.addEventListener("keydown", onKey);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [open]);

  if (!open) return null;

  return (
    <div className="waitlist-overlay" onClick={() => setOpen(false)} role="dialog" aria-modal="true" aria-label="Join the Waitlist">
      <div className="waitlist-overlay__card" onClick={(e) => e.stopPropagation()}>
        <button className="waitlist-overlay__close" aria-label="Close" onClick={() => setOpen(false)}>×</button>
        <WaitlistForm onSuccess={() => setOpen(false)} />
      </div>
    </div>
  );
}
