"use client";
import { useEffect, useState } from "react";
import { createSupabaseBrowser } from "@/lib/supabase/client";

// "Follow" toggle for encyclopedic pages — feeds the member dashboard's Followed Pages.
export function FollowButton({ itemId }: { itemId: number }) {
  const [supabase] = useState(() => createSupabaseBrowser());
  const [following, setFollowing] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    (async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;
      const { data } = await supabase.from("follows").select("id").eq("content_item_id", itemId).maybeSingle();
      setFollowing(!!data);
    })();
  }, [supabase, itemId]);

  async function toggle() {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) { window.location.href = "/login"; return; }
    setBusy(true);
    if (following) {
      await supabase.from("follows").delete().eq("content_item_id", itemId).eq("user_id", user.id);
      setFollowing(false);
    } else {
      await supabase.from("follows").insert({ content_item_id: itemId, user_id: user.id });
      setFollowing(true);
    }
    setBusy(false);
  }

  return (
    <button type="button" className="research-hero__center-tag" style={{ cursor: "pointer", border: "none", font: "inherit", opacity: busy ? 0.6 : 1 }} onClick={toggle}>
      {following ? "✓ Following" : "＋ Follow"}
    </button>
  );
}
