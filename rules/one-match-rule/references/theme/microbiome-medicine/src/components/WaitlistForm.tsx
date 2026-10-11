"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { createSupabaseBrowser } from "@/lib/supabase/client";

// The single "Join the Waitlist" signup form — rebuilt from the original theme
// (partials/auth/signup.php + signup-role-groups). Role radios reveal the
// matching bucket fields; submit creates the account, buckets the person, and
// signs them in immediately (server auto-confirms the email).

type Role = "clinician" | "researcher" | "int_ind";

function Field({
  name, label, placeholder, type = "text", required = false, value, onChange,
}: {
  name: string; label?: string; placeholder?: string; type?: string; required?: boolean;
  value: string; onChange: (v: string) => void;
}) {
  return (
    <div className="field" id={`field-${name}`}>
      {label && <label className="field__label" htmlFor={`rgbc-${name}`}>{label}</label>}
      <div className="field__box">
        <input
          className="field"
          name={name}
          id={`rgbc-${name}`}
          type={type}
          placeholder={placeholder}
          required={required}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          autoComplete={type === "password" ? "new-password" : type === "email" ? "email" : "off"}
        />
      </div>
    </div>
  );
}

export function WaitlistForm({ onSuccess }: { onSuccess?: () => void }) {
  const router = useRouter();
  const [supabase] = useState(() => createSupabaseBrowser());
  const [role, setRole] = useState<Role>("int_ind");
  const [f, setF] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const set = (k: string) => (v: string) => setF((p) => ({ ...p, [k]: v }));

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    if ((f.password || "") !== (f["password-confirm"] || "")) {
      setErr("Passwords do not match.");
      return;
    }
    setBusy(true);
    try {
      const res = await fetch("/api/waitlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...f, role }),
      });
      const data = await res.json();
      if (!res.ok) {
        setErr(data.error || "Something went wrong. Please try again.");
        setBusy(false);
        return;
      }
      // Auto-confirmed server-side → sign in immediately to unlock everything.
      const { error } = await supabase.auth.signInWithPassword({
        email: String(f.email || "").trim().toLowerCase(),
        password: f.password || "",
      });
      if (error) {
        setErr("Account created — please log in to continue.");
        setBusy(false);
        return;
      }
      if (onSuccess) {
        onSuccess();
        router.refresh();
      } else {
        router.push("/dashboard");
      }
    } catch {
      setErr("Network error. Please try again.");
      setBusy(false);
    }
  }

  return (
    <form className="auth-form auth-form--signup" onSubmit={submit}>
      <h2 className="auth-form__title">Join the Waitlist</h2>

      <div className="auth-form__row">
        <div className="role-selection">
          <label className="mbio-radio">
            <input type="radio" name="user_role" checked={role === "clinician"} onChange={() => setRole("clinician")} />
            <span>I&apos;m a Clinician</span>
          </label>
          <label className="mbio-radio">
            <input type="radio" name="user_role" checked={role === "researcher"} onChange={() => setRole("researcher")} />
            <span>I&apos;m a Researcher</span>
          </label>
          <label className="mbio-radio">
            <input type="radio" name="user_role" checked={role === "int_ind"} onChange={() => setRole("int_ind")} />
            <span>I&apos;m an Interested Individual</span>
          </label>
        </div>
      </div>

      <div className="auth-form__row">
        <Field name="name" label="Full Name" placeholder="John Doe" required value={f.name || ""} onChange={set("name")} />
      </div>
      <div className="auth-form__row">
        <Field name="email" label="Email" type="email" placeholder="example@mail.com" required value={f.email || ""} onChange={set("email")} />
      </div>
      <div className="auth-form__row">
        <Field name="user_country" label="Country" placeholder="USA" required value={f.user_country || ""} onChange={set("user_country")} />
      </div>
      <div className="auth-form__row">
        <Field name="user_interest_areas" label="Areas of Interest" placeholder="Nutrition, skin, women&apos;s health, mental health, etc." value={f.user_interest_areas || ""} onChange={set("user_interest_areas")} />
      </div>

      {role === "clinician" && (
        <div className="auth-form__group">
          <div className="auth-form__row"><Field name="user_clinic" label="Clinic / Hospital" required value={f.user_clinic || ""} onChange={set("user_clinic")} /></div>
          <div className="auth-form__row"><Field name="user_medical_specialty" label="Medical Specialty" placeholder="e.g., OB-GYN, gastro, dermatology" required value={f.user_medical_specialty || ""} onChange={set("user_medical_specialty")} /></div>
          <div className="auth-form__row"><Field name="user_license_id" label="Professional ID / License" placeholder="Optional — for CME or priority access" value={f.user_license_id || ""} onChange={set("user_license_id")} /></div>
          <div className="auth-form__row"><Field name="user_practice_country" label="Country of Practice" required value={f.user_practice_country || ""} onChange={set("user_practice_country")} /></div>
        </div>
      )}

      {role === "researcher" && (
        <div className="auth-form__group">
          <div className="auth-form__row"><Field name="user_institution" label="Affiliated Institution / Lab" required value={f.user_institution || ""} onChange={set("user_institution")} /></div>
          <div className="auth-form__row"><Field name="user_academic_role" label="Academic Role" placeholder="e.g., PhD candidate, PI, postdoc" required value={f.user_academic_role || ""} onChange={set("user_academic_role")} /></div>
          <div className="auth-form__row"><Field name="user_research_focus" label="Research Focus" required value={f.user_research_focus || ""} onChange={set("user_research_focus")} /></div>
          <div className="auth-form__row"><Field name="user_orchid_id" label="ORCID / ResearchGate ID" placeholder="Optional" value={f.user_orchid_id || ""} onChange={set("user_orchid_id")} /></div>
        </div>
      )}

      {role === "int_ind" && (
        <div className="auth-form__group">
          <div className="auth-form__row"><Field name="user_interest_reason" label="Why You're Interested" placeholder="e.g., personal health, family diagnosis" required value={f.user_interest_reason || ""} onChange={set("user_interest_reason")} /></div>
        </div>
      )}

      <div className="auth-form__row">
        <Field name="password" type="password" placeholder="Password" required value={f.password || ""} onChange={set("password")} />
      </div>
      <div className="auth-form__row">
        <Field name="password-confirm" type="password" placeholder="Confirm Password" required value={f["password-confirm"] || ""} onChange={set("password-confirm")} />
      </div>

      {err && <div className="auth-form__row"><div className="field__errors" style={{ position: "static" }}>{err}</div></div>}

      <div className="auth-form__row">
        <button className="btn btn--full" type="submit" disabled={busy}>
          {busy ? "…" : "Join the Waitlist"}
        </button>
      </div>
      <div className="auth-form__row">
        <p className="text-center">Already have an account? <a href="/login">Log in</a></p>
      </div>
    </form>
  );
}
