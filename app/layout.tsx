import type { Metadata } from "next";
import "./globals.css";
import "@/components/shared-theme/theme.css";
import "@/components/shared-theme/reading-modules.css";
import "@/styles/second-look.css";
import "@/styles/reader-profile.css";
import {ThemeShell} from "@/components/shared-theme/theme";
import {getChatGPTUser,chatGPTSignInPath} from "@/app/chatgpt-auth";
import {secondLookTheme} from "@/lib/theme/config";
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

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const user=await getChatGPTUser();
  const theme={...secondLookTheme,accountLink:user?{label:"Reader profile",href:"/account/profile"}:{label:"My research",href:"/account"},primaryAction:user?{label:"My research",href:"/account"}:{label:"Log in",href:chatGPTSignInPath("/guides/library")},navigation:[...secondLookTheme.navigation,{label:"Account",href:"/account",children:[{label:"Saved research",href:"/account"},{label:"My guides",href:"/guides/library"},{label:"Reader profile",href:"/account/profile"}]}]};
  return (
    <html lang="en">
      <body className="antialiased"><LayoutMetrics/><ThemeShell config={theme}>{children}</ThemeShell></body>
    </html>
  );
}
