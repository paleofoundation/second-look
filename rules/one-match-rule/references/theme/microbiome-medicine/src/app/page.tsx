import type { Metadata } from "next";
import { HomePage } from "@/components/home/HomePage";

export const revalidate = 3600;
export const metadata: Metadata = {
  alternates: { canonical: "https://microbiomemedicine.com" },
};

export default function Home() {
  return <HomePage />;
}
