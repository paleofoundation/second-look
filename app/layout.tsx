import type { Metadata } from "next";
import "./globals.css";
import "@/components/shared-theme/theme.css";
import "@/components/shared-theme/reading-modules.css";
import "@/styles/second-look.css";
import "@/components/shared-theme/guide-library.css";
import "@/styles/reader-profile.css";
import "@/components/shared-theme/article-reading.css";
import "@/styles/hero-art.css";
import {ThemeShell} from "@/components/shared-theme/theme";
import {getChatGPTUser,chatGPTSignInPath} from "@/app/chatgpt-auth";
import {secondLookTheme} from "@/lib/theme/config";
import {LayoutMetrics} from "@/components/layout-metrics";

export const metadata: Metadata = {
  metadataBase: new URL("https://remaprx.com"),
  title: {default: "Second Look — Drug repurposing, in context", template: "%s | Second Look"},
  description: "Explore the questions, original studies and limitations behind drug repurposing. A private evidence pilot.",
  robots: {index: false, follow: false},
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
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
