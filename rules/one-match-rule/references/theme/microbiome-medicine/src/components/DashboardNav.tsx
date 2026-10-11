"use client";
import { usePathname } from "next/navigation";

const items = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/dashboard/profile", label: "My Profile" },
  { href: "/dashboard/followed", label: "Followed Pages" },
  { href: "/dashboard/subscription", label: "Subscription & Purchases" },
  { href: "/dashboard/receipts", label: "Receipts & Invoices" },
];

export function DashboardNav({ email }: { email: string }) {
  const path = usePathname();
  return (
    <nav>
      <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
        {items.map((it) => {
          const active = path === it.href;
          return (
            <li key={it.href}>
              <a
                href={it.href}
                style={{
                  display: "block", padding: "0.7rem 1.5rem", fontSize: ".95rem",
                  color: active ? "#cc3333" : "#374151",
                  background: active ? "#fff" : "transparent",
                  fontWeight: active ? 600 : 400, textDecoration: "none",
                  borderLeft: active ? "3px solid #cc3333" : "3px solid transparent",
                }}
              >
                {it.label}
              </a>
            </li>
          );
        })}
      </ul>
      <form action="/auth/signout" method="post" style={{ padding: "1.25rem 1.5rem 0", marginTop: "1rem", borderTop: "1px solid #ececec" }}>
        <p style={{ fontSize: ".75rem", color: "#9ca3af", marginBottom: ".5rem", wordBreak: "break-all" }}>{email}</p>
        <button type="submit" style={{ background: "none", border: "none", color: "#cc3333", cursor: "pointer", fontSize: ".9rem", padding: 0 }}>Sign out</button>
      </form>
    </nav>
  );
}
