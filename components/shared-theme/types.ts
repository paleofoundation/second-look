import type { AnchorHTMLAttributes, ComponentType, ImgHTMLAttributes, ReactNode } from "react";

export type ThemeLink = { label: string; href: string };
export type ThemeNavItem = ThemeLink & { children?: ThemeNavItem[] };
export type ThemeImage = { src: string; alt: string; width: number; height: number };
export type ThemeAuthor = {
  id: string; name: string; role: string; bio: string;
  portrait?: ThemeImage; profileHref?: string; orcid?: string;
};
export type ThemeAdapters = {
  Link?: ComponentType<AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }>;
  Image?: ComponentType<ImgHTMLAttributes<HTMLImageElement>>;
  /** Host-owned usable search suggestions. No old endpoint or scientific data is embedded. */
  searchSuggestions?: (query: string) => Promise<ThemeLink[]>;
};
export type ThemeConfig = {
  schemaVersion: "1.0.0";
  /** Match the destination's main landmark; defaults to main-content. */
  mainId?: string;
  identity: { name: string; homeHref: string; logo?: ThemeImage };
  palette: {
    main: string; accent: string; pale: string;
    mainDark?: string; mainTint?: string; ink?: string; muted?: string; link?: string;
  };
  navigation: ThemeNavItem[];
  search: { action: string; param: string; label: string; placeholder: string };
  accountLink?: ThemeLink;
  primaryAction?: ThemeLink;
  footer: {
    columns: { title: string; links: ThemeLink[] }[];
    legal: ThemeLink[]; copyright: string; note?: string;
    /** Supply a working host form or honest link. The theme never captures an email itself. */
    subscribe?: { title: string; content: ReactNode };
  };
  adapters?: ThemeAdapters;
};
export type ThemeHomeContent = {
  hero: {
    title: string; intro: string; image: ThemeImage;
    caption?: { eyebrow: string; title: string };
    quickLinks?: ThemeLink[]; quickLinksLabel?: string;
    note?: { mark: string; title: string; text: string; link: ThemeLink };
  };
  principles: string[];
  collectionHeading: string; collectionIntro: string;
  collections: { number: string; eyebrow: string; title: string; copy: string; href: string; links: ThemeLink[] }[];
  method: { title: string; intro: string; link: ThemeLink; steps: { title: string; text: string }[] };
  research: { title: string; link: ThemeLink; items: { title: string; kind: string; href: string }[] };
  join?: { title: string; text: string; content: ReactNode };
};
export type ArticleHeroProps = {
  title: string; description?: ReactNode; breadcrumbs: ThemeLink[];
  art?: ThemeImage; leftContext?: ReactNode; author?: ThemeAuthor;
  /** One verified author block in the hero image/author area. Overrides author and creditSlot. */
  authorSlot?: ReactNode;
  /** @deprecated Alias for authorSlot. Since 0.1.1 this renders in the hero image area, never the right rail. */
  creditSlot?: ReactNode;
  updatedLabel?: string; snapshot?: ReactNode; actions?: ReactNode;
  kindLabel?: string;
};
export type ArticleLayoutProps = { hero: ArticleHeroProps; leftRail?: ReactNode; rightRail?: ReactNode; children: ReactNode };
export type ThemeHomeProps = { content: ThemeHomeContent };
export type DirectoryPageProps = { title: string; description: string; items: DirectoryItem[]; breadcrumbs?: ThemeLink[]; side?: ReactNode };
export type SectionNavGroup = { id: string; label: string; icon?: ReactNode; children?: { id: string; label: string }[] };
export type DirectoryItem = { id: string; title: string; href: string; description?: string; status?: string };
