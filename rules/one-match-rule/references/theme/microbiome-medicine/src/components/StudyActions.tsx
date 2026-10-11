"use client";
import { useEffect, useState } from "react";
import { createSupabaseBrowser } from "@/lib/supabase/client";

const tag: React.CSSProperties = { cursor: "pointer", border: "none", font: "inherit" };

// Study actions for Theory / Research-feed pages: Favorite (persisted), Download PDF, Copy Citation.
export function StudyActions({
  itemId,
  title,
  authors,
  year,
  url,
}: {
  itemId: number;
  title: string;
  authors: string[];
  year?: string;
  url: string;
}) {
  const [supabase] = useState(() => createSupabaseBrowser());
  const [fav, setFav] = useState(false);
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    (async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;
      const { data } = await supabase.from("favorites").select("id").eq("content_item_id", itemId).maybeSingle();
      setFav(!!data);
    })();
  }, [supabase, itemId]);

  async function toggleFav() {
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

  function copyCite() {
    const a = authors.length ? authors.join(", ") + ". " : "";
    const cite = `${a}${title}. Microbiome Medicine${year ? `. ${year}` : ""}.${url ? " " + url : ""}`;
    navigator.clipboard?.writeText(cite)
      .then(() => { setCopied(true); setTimeout(() => setCopied(false), 2000); })
      .catch(() => {});
  }

  return (
    <div className="research-hero__center-tags">
      <button type="button" className="research-hero__center-tag" style={{ ...tag, opacity: busy ? 0.6 : 1 }} onClick={toggleFav}>
        {fav ? "★ Favorited" : "☆ Favorite study"}
      </button>
      <button type="button" className="research-hero__center-tag" style={tag} onClick={() => window.print()}>
        ⬇ Download PDF
      </button>
      <button type="button" className="research-hero__center-tag" style={tag} onClick={copyCite}>
        {copied ? "✓ Copied!" : "⧉ Copy Citation"}
      </button>
    </div>
  );
}
