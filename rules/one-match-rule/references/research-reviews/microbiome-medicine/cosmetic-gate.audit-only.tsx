"use client";
import { useEffect } from "react";
import { createSupabaseBrowser } from "@/lib/supabase/client";

// Cosmetic account-wall: for logged-OUT visitors, blur any [data-gated] block and
// overlay a "Join the Waitlist" wall (which opens the signup modal). On login it
// reveals instantly. The text stays in the DOM (only CSS-blurred), so Google still
// indexes it — the SEO-safe gate.
const WALL =
  '<div class="rgbc-gate__wall"><div class="rgbc-gate__wall-inner">' +
  '<p class="rgbc-gate__wall-title">Create a free account to unlock this study summary.</p>' +
  '<a href="#join-waitlist" data-open-waitlist class="btn">Get started with your free account</a>' +
  '</div></div>';

function apply(locked: boolean) {
  document.querySelectorAll<HTMLElement>("[data-gated]").forEach((el) => {
    const wall = el.querySelector(":scope > .rgbc-gate__wall");
    if (locked) {
      el.classList.add("rgbc-gated--locked");
      if (!wall) el.insertAdjacentHTML("beforeend", WALL);
    } else {
      el.classList.remove("rgbc-gated--locked");
      wall?.remove();
    }
  });
}

export function AccessGate() {
  useEffect(() => {
    const supabase = createSupabaseBrowser();
    let mounted = true;
    // Use the LOCAL session (no network round-trip) so a slow/failed getUser() call
    // can't wrongly lock out a signed-in reader. The wall is cosmetic, so the local
    // session is the right signal.
    supabase.auth.getSession().then(({ data }) => {
      if (mounted) apply(!data.session);
    });
    const { data: sub } = supabase.auth.onAuthStateChange((_e, session) => apply(!session));
    return () => {
      mounted = false;
      sub.subscription.unsubscribe();
    };
  }, []);
  return null;
}
