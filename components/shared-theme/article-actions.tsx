import type {ReactNode} from 'react';

export type HeroActionLink = {
  label: string;
  href: string;
  /** Decorative, non-interactive icon. The visible label names the link. */
  icon?: ReactNode;
};

export type HeroActionsProps = {
  /** Host-owned save control, including its authentication and status behavior. */
  saveSlot?: ReactNode;
  /** Supply only links whose destination sections exist on this page. */
  links: readonly HeroActionLink[];
  ariaLabel?: string;
  className?: string;
};

/** ArticleHero supplies the outer research-hero__center-tags spacing. */
export function HeroActions({saveSlot, links, ariaLabel = 'Page actions', className}: HeroActionsProps) {
  if (saveSlot == null && links.length === 0) return null;

  return <nav className={['omr-hero-actions', className].filter(Boolean).join(' ')} aria-label={ariaLabel}>
    {saveSlot != null && <div className="omr-hero-actions__save">{saveSlot}</div>}
    {links.map(link => <a className="research-hero__center-tag omr-hero-action" href={link.href} key={`${link.href}:${link.label}`}>
      {link.icon != null && <span className="omr-hero-action__icon" aria-hidden="true">{link.icon}</span>}
      <span>{link.label}</span>
    </a>)}
  </nav>;
}
