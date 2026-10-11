import { createSupabaseServer } from "@/lib/supabase/server";
import { segmentForType } from "@/lib/content";

export const dynamic = "force-dynamic";

function fmtDate(d?: string | null) {
  if (!d) return "";
  return new Date(d).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" });
}

type CI = { title: string; slug: string; type: string; modified_at: string | null };

export default async function DashboardHome() {
  const supabase = await createSupabaseServer();
  const { data } = await supabase
    .from("favorites")
    .select("created_at, content_items(title, slug, type, modified_at)")
    .order("created_at", { ascending: false });

  const rows = (data ?? []).map((r) => {
    const ci = (Array.isArray(r.content_items) ? r.content_items[0] : r.content_items) as CI | undefined;
    return ci ? { title: ci.title, href: `/${segmentForType(ci.type)}/${ci.slug}`, updated: ci.modified_at } : null;
  }).filter(Boolean) as { title: string; href: string; updated: string | null }[];

  return (
    <section>
      <h1 style={{ fontSize: "1.9rem", marginBottom: "1.5rem", color: "#111" }}>Dashboard</h1>
      <h2 style={{ fontFamily: "var(--font-serif)", color: "#cc3333", fontSize: "1.4rem", borderBottom: "1px dashed #cbd5e1", paddingBottom: ".5rem", marginBottom: "1rem" }}>
        Favorite Study Summaries
      </h2>
      {rows.length === 0 ? (
        <p style={{ color: "#6b7280" }}>
          You haven&apos;t favorited any studies yet. Open a study summary or theory page and click <strong>☆ Favorite study</strong>.
        </p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#cc3333", color: "#fff", textAlign: "left" }}>
              <th style={{ padding: "0.7rem 1rem", fontWeight: 600 }}>Title</th>
              <th style={{ padding: "0.7rem 1rem", fontWeight: 600, width: 180 }}>Last Updated</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i} style={{ borderBottom: "1px solid #eee" }}>
                <td style={{ padding: "0.9rem 1rem" }}>
                  <a href={r.href} style={{ color: "#cc3333", textDecoration: "underline" }}>{r.title}</a>
                </td>
                <td style={{ padding: "0.9rem 1rem", color: "#cc3333" }}>{fmtDate(r.updated)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
