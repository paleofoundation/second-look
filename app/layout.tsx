import type { Metadata } from "next";
import "./globals.css";
import "@/components/shared-theme/theme.css";
import "@/components/shared-theme/reading-modules.css";
import "@/styles/second-look.css";
import "@/components/shared-theme/guide-library.css";
import "@/styles/guide-library.css";
import "@/styles/reader-profile.css";
import "@/components/shared-theme/article-reading.css";
import "@/components/shared-theme/article-sharing.css";
import "@/components/shared-theme/guide-reader.css";
import "@/styles/hero-art.css";
import "@/styles/treatment-suitability.css";
import {ThemeShell} from "@/components/shared-theme/theme";
import {getChatGPTUser,chatGPTSignInPath} from "@/app/chatgpt-auth";
import {secondLookTheme} from "@/lib/theme/config";
import {LayoutMetrics} from "@/components/layout-metrics";

export const metadata: Metadata = {
  metadataBase: new URL("https://remaprx.com"),
  title: {default: "RemapRx — The drug repurposing atlas", template: "%s | RemapRx"},
  description: "Mapping new targets for approved medications. Explore investigated uses, proposed mechanisms and source-linked findings in the drug repurposing atlas.",
  robots: "noindex,follow",
  openGraph: {type:"website", siteName:"RemapRx", title:"RemapRx — The drug repurposing atlas", description:"Mapping new targets for approved medications. Map each connection to its sources.", images:[{url:"/brand/remaprx-social.png",width:1200,height:630,alt:"RemapRx: Mapping new targets for approved medications."}]},
  twitter: {card:"summary_large_image", title:"RemapRx — The drug repurposing atlas", description:"Mapping new targets for approved medications. Map each connection to its sources.", images:["/brand/remaprx-social.png"]},
  manifest: "/manifest.webmanifest?v=remaprx-app-white-1",
  icons: {
    icon: [{url: "/favicon.svg?v=remaprx-site-yellow-1", type: "image/svg+xml"}, {url: "/favicon.ico?v=remaprx-site-yellow-1", sizes: "16x16 32x32 48x48", type: "image/x-icon"}],
    shortcut: "/favicon.ico?v=remaprx-site-yellow-1",
    apple: "/apple-touch-icon.png?v=remaprx-app-white-1",
  },
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const user=await getChatGPTUser();
  const theme={...secondLookTheme,accountLink:{label:"Account",href:"/account"},primaryAction:user?{label:"My guides",href:"/guides/library"}:{label:"Log in",href:chatGPTSignInPath("/guides/library")}};
  return (
    <html lang="en-US">
      <body className="antialiased"><LayoutMetrics/><ThemeShell config={theme}>{children}</ThemeShell></body>
    </html>
  );
}
