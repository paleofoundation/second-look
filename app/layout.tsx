import type { Metadata } from "next";
import "./globals.css";
import {LayoutMetrics} from "@/components/layout-metrics";

export const metadata: Metadata = {
  title: {default: "Second Look — Drug repurposing, in context", template: "%s | Second Look"},
  description: "Explore the questions, original studies and limitations behind drug repurposing. A private evidence pilot.",
  robots: {index: false, follow: false},
  other: {
    "codex-preview": "development",
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased"><LayoutMetrics/>{children}</body>
    </html>
  );
}
