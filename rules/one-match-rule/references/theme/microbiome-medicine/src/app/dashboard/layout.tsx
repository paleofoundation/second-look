import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { createSupabaseServer } from "@/lib/supabase/server";
import { DashboardNav } from "@/components/DashboardNav";
import { NOINDEX_ROBOTS } from "@/lib/seo";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { robots: NOINDEX_ROBOTS };

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const supabase = await createSupabaseServer();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  return (
    <div style={{ display: "flex", minHeight: "65vh", maxWidth: 1300, margin: "0 auto", width: "100%" }}>
      <aside style={{ width: 250, flexShrink: 0, background: "#f7f7f8", borderRight: "1px solid #ececec", padding: "1.5rem 0" }}>
        <DashboardNav email={user.email ?? ""} />
      </aside>
      <main style={{ flex: 1, minWidth: 0, padding: "1.5rem 2rem" }}>
        <div style={{ background: "#f8f9fb", borderLeft: "4px solid #cc3333", padding: "0.85rem 1.1rem", borderRadius: 4, marginBottom: "1.75rem" }}>
          <strong style={{ color: "#cc3333" }}>Microbiome+ unlocks everything on the site.</strong>{" "}
          <a href="/dashboard/subscription" style={{ color: "#cc3333", fontWeight: 600 }}>Try free for 7 days.</a>
        </div>
        {children}
      </main>
    </div>
  );
}
