export const dynamic = "force-dynamic";

export default function SubscriptionPage() {
  return (
    <section>
      <h1 style={{ fontSize: "1.9rem", marginBottom: "1.5rem", color: "#111" }}>Subscription &amp; Purchases</h1>

      <div style={{ border: "1px solid #ececec", borderRadius: 12, padding: "1.5rem", maxWidth: 560 }}>
        <p style={{ fontFamily: "var(--font-serif)", color: "#cc3333", fontSize: "1.3rem", marginBottom: ".25rem" }}>Microbiome+</p>
        <p style={{ color: "#374151", marginBottom: "1rem" }}>Unlocks every study summary, signature, and intervention on the site.</p>
        <p style={{ color: "#6b7280", fontSize: ".9rem", marginBottom: "1rem" }}>Current plan: <strong>Free</strong></p>
        <button style={{ padding: "0.65rem 1.4rem", background: "#cc3333", color: "#fff", border: "none", borderRadius: 8, fontWeight: 600, cursor: "pointer" }}>
          Start 7-day free trial
        </button>
      </div>

      <p style={{ marginTop: "1.5rem", color: "#9ca3af", fontSize: ".85rem", maxWidth: 560 }}>
        Note: paid checkout is processed by a payment provider (e.g. Stripe). Connecting the
        billing account activates the trial button and populates Receipts &amp; Invoices.
      </p>
    </section>
  );
}
