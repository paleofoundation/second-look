"use client";
import { useEffect, useState } from "react";
import { createSupabaseBrowser } from "@/lib/supabase/client";

const input: React.CSSProperties = { width: "100%", maxWidth: 520, padding: "0.6rem 0.75rem", border: "1px solid #d4d4d8", borderRadius: 8, fontSize: "0.95rem", marginTop: 4 };
const label: React.CSSProperties = { display: "block", fontSize: "0.85rem", fontWeight: 600, marginTop: "1.1rem", color: "#374151" };

export default function ProfilePage() {
  const [supabase] = useState(() => createSupabaseBrowser());
  const [displayName, setDisplayName] = useState("");
  const [bio, setBio] = useState("");
  const [email, setEmail] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    (async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;
      setEmail(user.email ?? "");
      const { data } = await supabase.from("profiles").select("display_name, bio").eq("id", user.id).single();
      if (data) { setDisplayName(data.display_name ?? ""); setBio(data.bio ?? ""); }
    })();
  }, [supabase]);

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setMsg(null);
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) { setBusy(false); return; }
    const { error } = await supabase.from("profiles").update({ display_name: displayName, bio }).eq("id", user.id);
    setMsg(error ? error.message : "Profile saved.");
    setBusy(false);
  }

  return (
    <section>
      <h1 style={{ fontSize: "1.9rem", marginBottom: "1.5rem", color: "#111" }}>My Profile</h1>
      <form onSubmit={save}>
        <label style={label}>Email
          <input style={{ ...input, background: "#f3f4f6", color: "#6b7280" }} value={email} disabled />
        </label>
        <label style={label}>Display name
          <input style={input} value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
        </label>
        <label style={label}>Bio
          <textarea style={{ ...input, minHeight: 110, resize: "vertical" }} value={bio} onChange={(e) => setBio(e.target.value)} />
        </label>
        <button type="submit" disabled={busy} style={{ marginTop: "1.25rem", padding: "0.6rem 1.5rem", background: "#cc3333", color: "#fff", border: "none", borderRadius: 8, fontWeight: 600, cursor: "pointer", opacity: busy ? 0.6 : 1 }}>
          {busy ? "Saving…" : "Save changes"}
        </button>
        {msg && <span style={{ marginLeft: "1rem", color: "#16a34a", fontSize: ".9rem" }}>{msg}</span>}
      </form>
    </section>
  );
}
