"use client";

/** Presentational extraction of the active Microbiome root, HomePage and ArticleView.
 * Source/override details live in theme-manifest.json, not in reader-facing copy. */
import React, { createContext, useContext, useEffect, useId, useRef, useState } from "react";
import type { CSSProperties, ReactNode } from "react";
import type { ArticleHeroProps, ArticleLayoutProps, DirectoryItem, DirectoryPageProps, SectionNavGroup, ThemeAuthor, ThemeConfig, ThemeHomeProps, ThemeImage, ThemeNavItem } from "./types";
import homeStyles from "./theme-home.module.css";
import { ArrowLeft, ArrowRight, ChevronDown, ChevronUp } from "lucide-react";
import { SectionIcon } from "./section-icon";

const ThemeContext = createContext<ThemeConfig | null>(null);
export function useThemeConfig(): ThemeConfig {
  const config = useContext(ThemeContext);
  if (!config) throw new Error("Theme components require ThemeShell or ThemeProvider.");
  return config;
}
export function ThemeProvider({ config, children }: { config: ThemeConfig; children: ReactNode }) {
  return <ThemeContext.Provider value={config}>{children}</ThemeContext.Provider>;
}
export function ThemeAnchor(props: React.AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) {
  const Link = useThemeConfig().adapters?.Link;
  return Link ? <Link {...props} /> : <a {...props} />;
}
function Image({ image, ...props }: { image: ThemeImage } & React.ImgHTMLAttributes<HTMLImageElement>) {
  const Adapter = useThemeConfig().adapters?.Image;
  return Adapter ? <Adapter {...image} {...props} /> : <img {...image} {...props} />;
}
function SearchIcon() {
  return <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true"><circle cx="10" cy="10" r="7" /><path d="m15 15 7 7" /></svg>;
}
function Brand({ mobile = false }: { mobile?: boolean }) {
  const { identity } = useThemeConfig();
  return <ThemeAnchor className="custom-logo-link img-middle" href={identity.homeHref} aria-label={`${identity.name} home`}>
    {identity.logo ? <Image image={identity.logo} className="img-autosize custom-logo" fetchPriority={mobile ? undefined : "high"} /> : <span className="omr-wordmark">{identity.name}</span>}
  </ThemeAnchor>;
}
export function ThemeSearch({ home = false }: { home?: boolean }) {
  const config = useThemeConfig();
  const id = useId();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<{ label: string; href: string }[]>([]);
  const [show, setShow] = useState(false);
  useEffect(() => {
    let current = true;
    const lookup = config.adapters?.searchSuggestions;
    if (!lookup || query.trim().length < 2) { setResults([]); return; }
    const timer = window.setTimeout(() => {
      lookup(query.trim()).then(items => { if (current) setResults(items); }).catch(() => { if (current) setResults([]); });
    }, 180);
    return () => { current = false; window.clearTimeout(timer); };
  }, [query, config.adapters]);
  return <form className={home ? `${homeStyles.search} omr-search` : "rgbc-search__form omr-search"} action={config.search.action} method="get" role="search"
    onBlur={event => { if (!event.currentTarget.contains(event.relatedTarget as Node | null)) setShow(false); }} onKeyDown={event => { if (event.key === "Escape") setShow(false); }}>
    <label className="sr-only" htmlFor={id}>{config.search.label}</label>
    <input className={home ? undefined : "rgbc-search__input field field--lg"} id={id} name={config.search.param} type="search" autoComplete="off" placeholder={config.search.placeholder} value={query}
      onChange={event => { setQuery(event.target.value); setShow(true); }} onFocus={() => setShow(true)} />
    <button className={home ? undefined : "rgbc-search__submit btn btn--lg"} type="submit" aria-label={config.search.label}><SearchIcon /></button>
    {show && results.length > 0 && <ul className="rgbc-search__items omr-search-suggestions" aria-label="Search suggestions">{results.map(item => <li key={item.href}><ThemeAnchor className="rgbc-search__link" href={item.href}>{item.label}</ThemeAnchor></li>)}</ul>}
  </form>;
}
function MegaMenuItem({item}: {item: ThemeNavItem}) {
  const [open,setOpen]=useState(false);
  const root=useRef<HTMLLIElement>(null);
  const trigger=useRef<HTMLButtonElement>(null);
  const id=useId();
  useEffect(()=>{
    if(!open)return;
    const outside=(event:PointerEvent)=>{if(!root.current?.contains(event.target as Node))setOpen(false)};
    document.addEventListener('pointerdown',outside);
    return()=>document.removeEventListener('pointerdown',outside);
  },[open]);
  const menu=item.mega!;
  return <li ref={root} className="omr-mega-item" onBlur={event=>{if(!event.currentTarget.contains(event.relatedTarget as Node|null))setOpen(false)}} onKeyDown={event=>{if(event.key==='Escape'&&open){event.preventDefault();event.stopPropagation();setOpen(false);trigger.current?.focus()}}}>
    <button ref={trigger} type="button" className="omr-mega-trigger" aria-expanded={open} aria-controls={id} onClick={()=>setOpen(value=>!value)} onKeyDown={event=>{if(event.key==='ArrowDown'){event.preventDefault();setOpen(true);requestAnimationFrame(()=>root.current?.querySelector<HTMLAnchorElement>('.omr-mega-panel a')?.focus())}}}>{item.label}<svg viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="m2 4 4 4 4-4"/></svg></button>
    <section className="omr-mega-panel" id={id} aria-label={item.label+' topics'} hidden={!open}>
      <div className="omr-mega-intro"><p>{menu.intro}</p><button type="button" aria-label={'Close '+item.label+' topics'} onClick={()=>{setOpen(false);trigger.current?.focus()}}>×</button></div>
      <div className="omr-mega-columns">{menu.columns.map(column=><div key={column.title}><h2>{column.title}</h2><ul>{column.links.map(link=><li key={link.href+link.label}><ThemeAnchor href={link.href} onClick={()=>setOpen(false)}>{link.label}{link.detail&&<small>{link.detail}</small>}</ThemeAnchor></li>)}</ul></div>)}</div>
      <div className="omr-mega-foot"><p>{menu.note}</p>{menu.allLink&&<ThemeAnchor href={menu.allLink.href} onClick={()=>setOpen(false)}>{menu.allLink.label}</ThemeAnchor>}</div>
    </section>
  </li>;
}
function MenuItem({ item, depth = 0 }: { item: ThemeNavItem; depth?: number }) {
  const [open, setOpen] = useState(false);
  const toggleButton = useRef<HTMLButtonElement>(null);
  const id = useId();
  const hasChildren = !!item.children?.length;
  return <li className={`menu-item${hasChildren ? " menu-item-has-children" : ""}${open ? " open" : ""}`}
    onMouseEnter={() => { if (window.matchMedia("(hover:hover)").matches) setOpen(true); }}
    onMouseLeave={event => { if (!event.currentTarget.contains(document.activeElement)) setOpen(false); }}
    onFocus={event => { if ((event.target as HTMLElement).tagName === "A" && window.matchMedia("(min-width:992px)").matches) setOpen(true); }}
    onBlur={event => { if (!event.currentTarget.contains(event.relatedTarget as Node | null)) setOpen(false); }}
    onKeyDown={event => { if (event.key === "Escape" && hasChildren && open) { event.stopPropagation(); setOpen(false); toggleButton.current?.focus(); } }}>
    <div className="omr-menu-label"><ThemeAnchor href={item.href}>{item.label}</ThemeAnchor>{hasChildren && <button ref={toggleButton} type="button" className="omr-menu-toggle" aria-label={`${open ? "Close" : "Open"} ${item.label} submenu`} aria-expanded={open} aria-controls={id} onClick={() => setOpen(value => !value)}><span aria-hidden="true">⌄</span></button>}</div>
    {hasChildren && <ul className="sub-menu" id={id} data-depth={depth}>{item.children!.map(child => <MenuItem item={child} depth={depth + 1} key={child.href + child.label} />)}</ul>}
  </li>;
}
export function ThemeHeader() {
  const config = useThemeConfig();
  const [open, setOpen] = useState(false);
  const nav = useRef<HTMLElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const id = useId();
  useEffect(() => {
    if (!open) return;
    const media = window.matchMedia("(max-width: 991.98px)");
    const old = document.body.style.overflow;
    if (media.matches) { document.body.style.overflow = "hidden"; nav.current?.querySelector<HTMLButtonElement>("button")?.focus(); }
    const close = () => { setOpen(false); trigger.current?.focus(); };
    const key = (event: KeyboardEvent) => {
      if (event.key === "Escape") { event.preventDefault(); close(); }
      if (event.key !== "Tab" || !media.matches) return;
      const elements = Array.from(nav.current?.querySelectorAll<HTMLElement>('a[href],button,input') || []).filter(el => el.getClientRects().length > 0);
      const first = elements[0], last = elements[elements.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    };
    const resize = () => { if (!media.matches) setOpen(false); };
    document.addEventListener("keydown", key); media.addEventListener("change", resize);
    return () => { document.body.style.overflow = old; document.removeEventListener("keydown", key); media.removeEventListener("change", resize); };
  }, [open]);
  return <header className="header"><div className="header__wrapper wrapper">
    <button ref={trigger} className="header__burger" type="button" aria-label="Open menu" aria-expanded={open} aria-controls={id} onClick={() => setOpen(true)}>Menu</button>
    <div className="header__logo"><Brand /></div>
    {open && <button className="omr-menu-backdrop" tabIndex={-1} aria-label="Close menu" onClick={() => { setOpen(false); trigger.current?.focus(); }} />}
    <div className="header__menu"><nav ref={nav} id={id} aria-label="Main navigation" className={`header__nav${open ? " is-open" : ""}`} onClick={event => { if ((event.target as HTMLElement).closest("a")) setOpen(false); }}>
      <div className="header__mobile-logo"><Brand mobile /><button className="header__close" type="button" aria-label="Close menu" onClick={() => { setOpen(false); trigger.current?.focus(); }}>×</button></div>
      <ThemeSearch /><ThemeAnchor className="header__search" href={config.search.action}><span>Search</span><SearchIcon /></ThemeAnchor>
      <div className="menu-main-container"><ul className="menu">{config.navigation.map(item => item.mega ? <MegaMenuItem key={item.href + item.label} item={item}/> : <MenuItem key={item.href + item.label} item={item} />)}</ul></div>
    </nav></div>
    <div className="header__actions">{config.accountLink && <ThemeAnchor className="header__login" href={config.accountLink.href}>{config.accountLink.label}</ThemeAnchor>}{config.primaryAction && <ThemeAnchor className="btn" href={config.primaryAction.href}>{config.primaryAction.label}</ThemeAnchor>}</div>
  </div></header>;
}
export function ThemeFooter() {
  const { identity, footer } = useThemeConfig();
  const subscription = footer.subscribe && <div className="footer__form-wrapper"><h3 className="footer__title">{footer.subscribe.title}</h3>{footer.subscribe.content}</div>;
  return <footer className="footer"><div className="footer__wrapper wrapper">
    <div className="footer__left"><div className="footer__logo"><ThemeAnchor className="custom-logo-link img-middle" href={identity.homeHref}>{identity.name}</ThemeAnchor></div>
      <div className="footer__tagline"><div className="footer__copyrights"><p>{footer.copyright}</p>{footer.note && <p>{footer.note}</p>}</div><div className="footer__links">{footer.legal.map((link, index) => <React.Fragment key={link.href}>{index > 0 && <span className="footer__links-separator" aria-hidden="true">|</span>}<ThemeAnchor className="footer__links-item" href={link.href}>{link.label}</ThemeAnchor></React.Fragment>)}</div></div>
      {subscription && <div className="footer__form-wrapper_mobile">{subscription}</div>}
    </div>
    <div className="footer__center">{footer.columns.map(column => <div className="footer__column" key={column.title}><h3 className="footer__title">{column.title}</h3><ul className="footer__menu">{column.links.map(link => <li className="menu-item" key={link.href}><ThemeAnchor href={link.href}>{link.label}</ThemeAnchor></li>)}</ul></div>)}</div>
    {subscription && <div className="footer__right">{subscription}</div>}
  </div></footer>;
}
export function ThemeShell({ config, children }: { config: ThemeConfig; children: ReactNode }) {
  const p = config.palette;
  const style = { "--color-primary": p.main, "--color-primary-dark": p.mainDark || p.main, "--color-primary-600": p.mainDark || p.main, "--color-primary-500": p.main,
    "--color-primary-100": p.mainTint || p.pale, "--color-primary-200": p.mainTint || p.pale, "--omr-main": p.main, "--omr-accent": p.accent, "--omr-pale": p.pale,
    "--omr-ink": p.ink || "#1a1a2e", "--omr-muted": p.muted || "#6c757d", "--omr-link": p.link || p.main } as CSSProperties;
  return <ThemeProvider config={config}><div className="omr-theme" style={style}><a className="omr-skip" href={`#${config.mainId || "main-content"}`}>Skip to content</a><ThemeHeader />{children}<ThemeFooter /></div></ThemeProvider>;
}
const h = (names: string) => names.split(" ").map(name => homeStyles[name]).join(" ");
export function ThemeHome({ content }: ThemeHomeProps) {
  const config = useThemeConfig();
  const { hero, collections, method, research } = content;
  return <main className={homeStyles.home} id={config.mainId || "main-content"}>
    <section className={h("hero")} id="top"><div className={h("hero__copy")}><h1>{hero.title}</h1><p className={h("hero__intro")}>{hero.intro}</p><ThemeSearch home />
      {!!hero.quickLinks?.length && <div className={h("quick-searches")}><span>{hero.quickLinksLabel || "Start exploring"}</span>{hero.quickLinks.map(link => <ThemeAnchor key={link.href} href={link.href}>{link.label}</ThemeAnchor>)}</div>}
    </div><div className={h("hero__media")}><div className={h("image-frame")}>{hero.image && <Image image={hero.image} sizes="(max-width: 1023px) 100vw, 42vw" fetchPriority="high" />}{hero.caption && <div className={h("image-caption")}><span>{hero.caption.eyebrow}</span><strong>{hero.caption.title}</strong></div>}</div>
      {hero.note && <div className={h("evidence-note")}><span className={h("evidence-note__mark")}>{hero.note.mark}</span><p><strong>{hero.note.title}</strong><br />{hero.note.text}</p><ThemeAnchor href={hero.note.link.href} aria-label={hero.note.link.label}>→</ThemeAnchor></div>}
    </div></section>
    <section className={h("credibility")} aria-label="Platform principles">{content.principles.map(principle => <span key={principle}>{principle}</span>)}</section>
    <section className={h("section")} id="explore"><div className={h("section-intro centered")}><h2>{content.collectionHeading}</h2><p>{content.collectionIntro}</p></div><div className={h("collection-grid")}>{collections.map(collection => <article className={h("collection-card")} key={collection.number}><div className={h("collection-card__top")}><span>{collection.number}</span><small>{collection.eyebrow}</small></div><h3>{collection.title}</h3><p>{collection.copy}</p><ul>{collection.links.map(link => <li key={link.href}><ThemeAnchor className="rgbc-archive__link" href={link.href}>{link.label}</ThemeAnchor></li>)}</ul><ThemeAnchor href={collection.href} className={h("card-link")}>See all</ThemeAnchor></article>)}</div></section>
    <section className={h("method section")} id="method"><div className={h("method__heading")}><h2>{method.title}</h2><p>{method.intro}</p><ThemeAnchor href={method.link.href} className={h("text-link")}>{method.link.label}<span>→</span></ThemeAnchor></div><ol className={h("method__steps")}>{method.steps.map((step, index) => <li key={step.title}><span>{String(index + 1).padStart(2, "0")}</span><div><h3>{step.title}</h3><p>{step.text}</p></div></li>)}</ol></section>
    <section className={h("section")} id="research"><div className={h("research__head")}><div><h2>{research.title}</h2></div><ThemeAnchor href={research.link.href} className={h("outline-button")}>{research.link.label}<span>→</span></ThemeAnchor></div><div className={h("research-list") + " rgbc-content__details-content"}>{research.items.map(item => <ThemeAnchor className={h("research-row")} href={item.href} key={item.href}><p>{item.title}</p><div className="rgbc-content__details-meta"><small className="rgbc-content__details-date">{item.kind}</small></div></ThemeAnchor>)}</div></section>
    {content.guides && <section className={h("section")} id="guides"><div className={h("research__head")}><div><span className="eyebrow">{content.guides.label}</span><h2>{content.guides.title}</h2><p>{content.guides.text}</p></div><ThemeAnchor className={h("outline-button")} href={content.guides.link.href}>{content.guides.link.label}</ThemeAnchor></div><div className={h("collection-grid")}>{content.guides.items.map(item=><article className={h("collection-card")} key={item.href}><small>{item.status}</small><h3><ThemeAnchor href={item.href}>{item.title}</ThemeAnchor></h3><p>{item.description}</p></article>)}</div></section>}
    {content.join && <section className={h("membership section")} id="membership"><div><h2>{content.join.title}</h2><p>{content.join.text}</p>{content.join.content}</div></section>}
  </main>;
}
/** All author surfaces share the same small green iD mark and canonical identity link. */
export function OrcidLink({ orcid, name }: { orcid?: string; name: string }) {
  const id = orcid?.trim().replace(/^https?:\/\/orcid\.org\//i, "").replace(/\/$/, "");
  if (!id || !/^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$/i.test(id)) return <span className="omr-author__missing">ORCID iD not supplied</span>;
  return <a className="omr-orcid" href={`https://orcid.org/${id}`} rel="noopener noreferrer" target="_blank" aria-label={`${name} ORCID iD ${id}`}>
    <svg width="20" height="20" viewBox="0 0 256 256" aria-hidden="true" focusable="false"><circle cx="128" cy="128" r="128" fill="#A6CE39" /><path fill="#fff" d="M86 186H70V80h16v106Zm-8-121a10 10 0 1 1 0-20 10 10 0 0 1 0 20Zm33 15h41c39 0 59 25 59 53s-20 53-59 53h-41V80Zm16 15v76h24c29 0 44-16 44-38s-15-38-44-38h-24Z" /></svg>
    <span>ORCID iD · {id}</span>
  </a>;
}
export function AuthorCard({ author }: { author: ThemeAuthor }) {
  const [open, setOpen] = useState(false);
  const id = useId();
  const card = useRef<HTMLDivElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const returningFocus = useRef(false);
  const close = () => { setOpen(false); if (document.activeElement !== trigger.current) { returningFocus.current = true; trigger.current?.focus({ preventScroll: true }); } };

  return <div ref={card} className="omr-author" onMouseLeave={() => { if (!card.current?.contains(document.activeElement)) setOpen(false); }} onBlur={event => { if (!event.currentTarget.contains(event.relatedTarget as Node | null)) setOpen(false); }} onKeyDown={event => { if (event.key === "Escape" && open) { event.stopPropagation(); close(); } }}>
    <button ref={trigger} type="button" className="omr-author__portrait" aria-expanded={open} aria-controls={id} aria-label={`About ${author.name}`} onMouseEnter={() => setOpen(true)} onFocus={() => { if (returningFocus.current) { returningFocus.current = false; return; } setOpen(true); }} onClick={() => setOpen(true)}>
      {author.portrait ? <Image image={author.portrait} /> : <span>Portrait not supplied</span>}
    </button>
    <div className="omr-author__identity"><small>{author.role}</small><div>{author.profileHref ? <ThemeAnchor href={author.profileHref}>{author.name}</ThemeAnchor> : author.name}<OrcidLink orcid={author.orcid} name={author.name} /></div></div>
    <div className="omr-author__bio" id={id} hidden={!open}><strong>{author.name}</strong><p>{author.bio || "Biography not supplied."}</p>{author.profileHref && <ThemeAnchor href={author.profileHref}>Read author profile</ThemeAnchor>}<button type="button" onClick={close} aria-label="Close author biography">×</button></div>
  </div>;
}
function Breadcrumbs({ items, label }: { items: { label: string; href: string }[]; label?: string }) {
  return <nav className="breadcrumb" aria-label="Breadcrumb"><ol className="breadcrumb__wrapper">{items.map(item => <li className="breadcrumb__item" key={item.href}><ThemeAnchor className="breadcrumb__link" href={item.href}>{item.label}</ThemeAnchor></li>)}{label && <li className="breadcrumb__item"><span className="breadcrumb_last"><span className="badge">{label}</span></span></li>}</ol></nav>;
}
export function ArticleHero({ title, description, breadcrumbs, art, leftContext, author, authorSlot, creditSlot, updatedLabel, snapshot, actions, kindLabel }: ArticleHeroProps) {
  const authorContent = authorSlot !== undefined ? authorSlot : creditSlot !== undefined ? creditSlot : author ? <AuthorCard author={author} /> : null;
  const hasAuthor = authorContent !== null && authorContent !== undefined && authorContent !== false;
  return <div className={`research-hero${hasAuthor ? " research-hero--with-author" : ""}`}><div className="research-hero__wrapper">
    <div className="research-hero__left" data-hero-region="image">{art && <Image image={art} className="research-hero__left-image" />}{leftContext && <div className="research-hero__left-content">{leftContext}</div>}</div>
    <div className="research-hero__center"><Breadcrumbs items={breadcrumbs} label={kindLabel} /><div className="research-hero__center-content"><h1 className="research-hero__center-title">{title}</h1>{description && <div className="research-hero__center-text">{description}</div>}</div>{actions && <div className="research-hero__center-tags">{actions}</div>}</div>
    <aside className="research-hero__right" data-hero-region="author-snapshot" aria-label="Author and article snapshot">{hasAuthor && <div className="research-hero__author">{authorContent}</div>}{updatedLabel && <p className="omr-updated">{updatedLabel}</p>}{snapshot}</aside>
  </div></div>;
}
export function ArticleLayout({ hero, leftRail, rightRail, children }: ArticleLayoutProps) {
  const config = useThemeConfig();
  return <main className="main omr-article" id={config.mainId || "main-content"}><ArticleHero {...hero} /><div className="research-content"><div className="research-content__wrapper">
    {leftRail || <div className="research-content__left omr-empty-rail" aria-hidden="true" />}
    <article className="research-content__center entry-content">{children}</article>
    <aside className="research-content__right" aria-label="Related reading">{rightRail}</aside>
  </div></div></main>;
}
export function ThemeSectionNav({ groups }: { groups: SectionNavGroup[] }) {
  const [active, setActive] = useState("");
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [collapsed, setCollapsed] = useState(false);
  useEffect(() => {
    const ids = groups.flatMap(group => [group.id, ...(group.children || []).map(child => child.id)]);
    const onScroll = () => { let current = ""; for (const id of ids) { const el = document.getElementById(id); if (el && el.getClientRects().length) { const offset = (parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) || 0) + (parseFloat(getComputedStyle(el).scrollMarginTop) || 0); if (el.getBoundingClientRect().top <= Math.max(140, offset + 2)) current = id; } } setActive(current || ids[0] || ""); };
    onScroll(); window.addEventListener("scroll", onScroll, { passive: true }); return () => window.removeEventListener("scroll", onScroll);
  }, [groups]);
  return <nav className={`research-content__left${collapsed ? " collapsed" : ""}`} aria-label="On this page"><div className="research-content__left-menu">
    <button type="button" className="research-content__left-btn" aria-label={collapsed ? "Expand contents" : "Collapse contents"} aria-expanded={!collapsed} onClick={() => setCollapsed(value => !value)}>{collapsed ? <ArrowRight aria-hidden="true"/> : <ArrowLeft aria-hidden="true"/>}</button>
    <div className="post-content__list post-sidebar" hidden={collapsed}>{groups.map(group => <div key={group.id}><div className="post-content__item post-content__item--h2"><span className="post-content__title omr-toc-label"><a className={`post-content__link${active === group.id ? " post-content__link--active" : ""}`} href={`#${group.id}`} aria-current={active === group.id ? "location" : undefined}><span className="omr-toc-icon" aria-hidden="true">{group.icon || <SectionIcon label={group.label}/>}</span><span>{group.label}</span></a>{!!group.children?.length && <button type="button" aria-label={`${expanded.has(group.id) ? "Collapse" : "Expand"} ${group.label}`} aria-expanded={expanded.has(group.id)} onClick={() => setExpanded(previous => { const next = new Set(previous); if (next.has(group.id)) next.delete(group.id); else next.add(group.id); return next; })}>{expanded.has(group.id) ? <ChevronUp aria-hidden="true"/> : <ChevronDown aria-hidden="true"/>}</button>}</span></div>{group.children?.map(child => <div key={child.id} className={`post-content__item post-content__item--h3${expanded.has(group.id) ? " active" : ""}`}><span className="post-content__title"><a className={`post-content__link${active === child.id ? " post-content__link--active" : ""}`} href={`#${child.id}`} aria-current={active === child.id ? "location" : undefined}>{child.label}</a></span></div>)}</div>)}</div>
  </div></nav>;
}
export function DirectoryPage({ title, description, items, breadcrumbs = [], side }: DirectoryPageProps) {
  const config = useThemeConfig();
  const groups = new Map<string, DirectoryItem[]>();
  [...items].sort((a, b) => a.title.localeCompare(b.title)).forEach(item => { const first = item.title.trim()[0]?.toUpperCase() || "#"; const key = /^[A-Z]$/.test(first) ? first : "#"; groups.set(key, [...(groups.get(key) || []), item]); });
  const letters = [...groups.keys()].sort();
  return <main className="main" id={config.mainId || "main-content"}><div className="rgbc-hero"><div className="rgbc-hero__wrapper wrapper"><div className="rgbc-hero__center rgbc-hero__center--archive"><Breadcrumbs items={breadcrumbs} /><div className="rgbc-hero__content"><h1 className="rgbc-hero__title">{title}</h1><p className="rgbc-hero__excerpt">{description}</p></div></div></div></div>
    <section className="rgbc-content"><div className="rgbc-content__wrapper wrapper"><div className="rgbc-content__main rgbc-archive"><h2 className="rgbc-archive__title">{items.length} {title}</h2><nav className="rgbc-archive__letters" aria-label="Jump to letter">{letters.map(letter => <a key={letter} className="rgbc-archive__item" href={`#letter-${letter === "#" ? "other" : letter}`}>{letter}</a>)}</nav>{letters.map(letter => <section className="omr-directory-group" key={letter}><div className="rgbc-archive__header" id={`letter-${letter === "#" ? "other" : letter}`}><h3 className="rgbc-archive__letter">{letter}</h3></div>{groups.get(letter)!.map(item => <div className="rgbc-archive__post" key={item.id}><ThemeAnchor className="rgbc-archive__link" href={item.href}>{item.title}</ThemeAnchor>{item.description && <p className="omr-directory-description">{item.description}</p>}{item.status && <small className="omr-directory-status">{item.status}</small>}</div>)}</section>)}</div>{side && <aside className="rgbc-content__side">{side}</aside>}</div></section>
  </main>;
}
