import type { Metadata } from "next";
import "./globals.css";
import "@/styles/theme-wp.css";
import { HEADER_HTML, FOOTER_HTML } from "@/theme/themeHtml";
import { Feedback } from "@/components/Feedback";
import { ScrollToTop } from "@/components/ScrollToTop";
import { HeaderSearch } from "@/components/HeaderSearch";
import { SearchAutocomplete } from "@/components/SearchAutocomplete";
import { WaitlistModal } from "@/components/WaitlistModal";
import { AccessGate } from "@/components/AccessGate";
import { unslashInternalHrefs } from "@/lib/seoIndexing";

export const metadata: Metadata = {
  metadataBase: new URL("https://microbiomemedicine.com"),
  title: {
    default: "Microbiome Medicine",
    template: "%s — Microbiome Medicine",
  },
  openGraph: {
    siteName: "Microbiome Medicine",
    type: "website",
    // Sitewide default social card; per-page buildMetadata images override it.
    images: [{ url: "/og-default.webp", width: 1200, height: 630, alt: "Microbiome Medicine" }],
  },
  twitter: { card: "summary_large_image", images: ["/og-default.webp"] },
  description:
    "A research-grounded reference on the human microbiome — microbes, conditions, interventions, and the evidence connecting them.",
};

// Point the header search form at our search route, and the account/membership
// links at the member dashboard. Also swap the captured logo (both the desktop and mobile
// <img>, matched by the shared `custom-logo` class) for the on-brand maroon Microbiome
// Medicine wordmark SVG — the old PNG was the brighter-red pre-rebrand asset.
const LOGO_IMG =
  '<img width="1096" height="208" src="/wp-content/uploads/2025/12/microbiome-medicine-logo.svg" class="img-autosize custom-logo" alt="Microbiome Medicine logo" decoding="async" fetchpriority="high" />';
const headerHtml = unslashInternalHrefs(
  HEADER_HTML
    .replace(/action="\/"/g, 'action="/search"')
    .replace(/href="\/auth\/login\/"/g, 'href="/dashboard"')
    .replace(/href="\/membership-2\/"/g, 'href="/dashboard/subscription"')
    .replace(/<img\b[^>]*\bcustom-logo\b[^>]*>/g, LOGO_IMG)
);

// Wire the footer newsletter forms to our subscribe endpoint, and correct the stale brand in
// the captured footer copyright (we rebranded to Microbiome Medicine / microbiomemedicine.com).
const footerHtml = unslashInternalHrefs(
  FOOTER_HTML
    .replace(/<form class="subscribe[^"]*js-subscribe-form"/g, '$& action="/api/subscribe" method="post"')
    .replace(/<input type="email" class="subscribe__input"/g, '<input type="email" name="email" class="subscribe__input"')
    .replace("© 2023–2026 MicrobiomeSignatures.com", "© 2023–2026 Microbiome Medicine")
);

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Lora:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <div dangerouslySetInnerHTML={{ __html: headerHtml }} />
        {children}
        <div dangerouslySetInnerHTML={{ __html: footerHtml }} />
        <Feedback />
        <ScrollToTop />
        <HeaderSearch />
        <SearchAutocomplete />
        <WaitlistModal />
        <AccessGate />
      </body>
    </html>
  );
}
