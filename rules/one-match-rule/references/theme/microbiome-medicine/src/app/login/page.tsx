"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { createSupabaseBrowser } from "@/lib/supabase/client";

const input: React.CSSProperties = {
  width: "100%", padding: "0.6rem 0.75rem", border: "1px solid #d4d4d8",
  borderRadius: 8, fontSize: "0.95rem", marginTop: 4,
};
const label: React.CSSProperties = { display: "block", fontSize: "0.85rem", fontWeight: 600, marginTop: "0.9rem", color: "#374151" };

export default function LoginPage() {
  const router = useRouter();
  const [supabase] = useState(() => createSupabaseBrowser());
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setMsg(null);
    if (mode === "signin") {
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) setMsg(error.message);
      else {
        router.push("/dashboard");
        router.refresh();
      }
    } else {
      const { error } = await supabase.auth.signUp({
        email,
        password,
        options: { emailRedirectTo: `${location.origin}/auth/callback` },
      });
      if (error) setMsg(error.message);
      else setMsg("Account created — check your email to confirm, then sign in.");
    }
    setBusy(false);
  }

  async function magicLink() {
    if (!email) { setMsg("Enter your email address first."); return; }
    setBusy(true);
    setMsg(null);
    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: { emailRedirectTo: `${location.origin}/auth/callback` },
    });
    setMsg(error ? error.message : "Magic link sent — check your email.");
    setBusy(false);
  }

  return (
    <div style={{ maxWidth: 420, margin: "3rem auto", padding: "0 1.25rem" }}>
      <div style={{ border: "1px solid #ececec", borderRadius: 14, padding: "2rem", boxShadow: "0 8px 30px rgba(0,0,0,.06)" }}>
        <h1 style={{ fontFamily: "var(--font-serif)", color: "#cc3333", fontSize: "1.6rem", marginBottom: ".25rem" }}>
          {mode === "signin" ? "Sign in" : "Create your account"}
        </h1>
        <p style={{ color: "#6b7280", fontSize: ".9rem", marginBottom: ".5rem" }}>
          Access your dashboard, favorites, and followed pages.
        </p>
        <form onSubmit={submit}>
          <label style={label}>Email
            <input style={input} type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" />
          </label>
          <label style={label}>Password
            <input style={input} type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} autoComplete={mode === "signin" ? "current-password" : "new-password"} />
          </label>
          <button type="submit" disabled={busy} style={{ width: "100%", marginTop: "1.2rem", padding: "0.7rem", background: "#cc3333", color: "#fff", border: "none", borderRadius: 8, fontWeight: 600, fontSize: "1rem", cursor: "pointer", opacity: busy ? 0.6 : 1 }}>
            {busy ? "…" : mode === "signin" ? "Sign in" : "Sign up"}
          </button>
        </form>
        <button onClick={magicLink} disabled={busy} style={{ width: "100%", marginTop: "0.6rem", padding: "0.65rem", background: "#fff", color: "#cc3333", border: "1px solid #cc3333", borderRadius: 8, fontWeight: 600, cursor: "pointer" }}>
          Email me a magic link
        </button>
        {msg && <p style={{ marginTop: "1rem", fontSize: ".88rem", color: "#b45309", background: "#fffbeb", padding: ".6rem .8rem", borderRadius: 8 }}>{msg}</p>}
        <p style={{ marginTop: "1.25rem", fontSize: ".88rem", color: "#6b7280", textAlign: "center" }}>
          {mode === "signin" ? "No account yet? " : "Already have an account? "}
          <button onClick={() => { setMode(mode === "signin" ? "signup" : "signin"); setMsg(null); }} style={{ background: "none", border: "none", color: "#183fab", cursor: "pointer", fontWeight: 600 }}>
            {mode === "signin" ? "Create one" : "Sign in"}
          </button>
        </p>
      </div>
    </div>
  );
}
