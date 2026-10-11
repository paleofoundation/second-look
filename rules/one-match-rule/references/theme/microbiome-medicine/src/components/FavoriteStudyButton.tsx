"use client";
import { useEffect, useState } from "react";
import { createSupabaseBrowser } from "@/lib/supabase/client";

// Single "Favorite study" button (WP feed pages use one button, not three).
export function FavoriteStudyButton({ itemId }: { itemId: number }) {
  const [supabase] = useState(() => createSupabaseBrowser());
  const [fav, setFav] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    (async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;
      const { data } = await supabase.from("favorites").select("id").eq("content_item_id", itemId).maybeSingle();
      setFav(!!data);
    })();
  }, [supabase, itemId]);

  async function toggle() {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) { window.location.href = "/login"; return; }
    setBusy(true);
    if (fav) {
      await supabase.from("favorites").delete().eq("content_item_id", itemId).eq("user_id", user.id);
      setFav(false);
    } else {
      await supabase.from("favorites").insert({ content_item_id: itemId, user_id: user.id });
      setFav(true);
    }
    setBusy(false);
  }

  return (
    <button type="button" className="research-hero__center-tag" style={{ cursor: "pointer", border: "none", font: "inherit", opacity: busy ? 0.6 : 1 }} onClick={toggle}>
      <svg xmlns="http://www.w3.org/2000/svg" fill={fav ? "currentColor" : "none"} viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" width={18} height={18} style={{ verticalAlign: "middle", marginRight: 6 }}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
      </svg>
      {fav ? "Favorited" : "Favorite study"}
    </button>
  );
}
