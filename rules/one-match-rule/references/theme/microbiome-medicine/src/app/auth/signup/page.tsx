import type { Metadata } from "next";
import { WaitlistForm } from "@/components/WaitlistForm";

export const metadata: Metadata = {
  title: "Join the Waitlist",
  robots: { index: false, follow: false },
  alternates: { canonical: "/auth/signup" },
};

// The signup page (same form as the modal). Linked from the right-rail
// "Join the Roundtable" box; replaces the old 404'd /auth/signup.
export default function SignupPage() {
  return (
    <div className="site-content">
      <main className="main">
        <div style={{ maxWidth: 600, margin: "3rem auto", padding: "0 1.25rem" }}>
          <div style={{ background: "#fff", border: "1px solid #ececec", borderRadius: 14, padding: "2.5rem", boxShadow: "0 8px 30px rgba(0,0,0,.06)" }}>
            <WaitlistForm />
          </div>
        </div>
      </main>
    </div>
  );
}
