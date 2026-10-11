import type { Metadata } from "next";
import { articleMetadata } from "@/components/ArticleView";
import { ResearchFeedView } from "@/components/ResearchFeedView";

export const revalidate = 3600;

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  return articleMetadata("research-feeds", slug);
}

export default async function Page({ params }: Props) {
  const { slug } = await params;
  return <ResearchFeedView slug={slug} />;
}
