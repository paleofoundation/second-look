import type { ReactNode } from "react";
import type { AuthorBio } from "@/theme/authorsBios";

// "Connect" row for the author hero — white outline icons on the red hero
// (fill white on hover -> red glyph). Monochrome (currentColor) so they match.
const Orcid = (
  <svg viewBox="0 0 256 256" aria-hidden="true">
    <path fill="currentColor" d="M86.3 186.2H70.9V79.1h15.4v107.1zM108.9 79.1h41.6c39.6 0 57 28.3 57 53.6 0 27.5-21.5 53.6-56.8 53.6h-41.8V79.1zm15.4 93.3h24.5c34.9 0 42.9-26.5 42.9-39.7 0-21.5-13.7-39.7-43.7-39.7h-23.7v79.4zM88.7 56.8c0 5.5-4.5 10.1-10.1 10.1s-10.1-4.6-10.1-10.1c0-5.6 4.5-10.1 10.1-10.1s10.1 4.6 10.1 10.1z" />
  </svg>
);
const Globe = (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path fill="currentColor" d="M12 2a10 10 0 100 20 10 10 0 000-20zm6.92 6h-2.95a15.7 15.7 0 00-1.38-3.56A8.03 8.03 0 0118.92 8zM12 4.04c.83 1.2 1.48 2.53 1.91 3.96h-3.82c.43-1.43 1.08-2.76 1.91-3.96zM4.26 14a7.96 7.96 0 010-4h3.38a16.6 16.6 0 000 4H4.26zm.82 2h2.95c.32 1.25.78 2.45 1.38 3.56A7.99 7.99 0 015.08 16zm2.95-8H5.08a7.99 7.99 0 014.33-3.56A15.7 15.7 0 008.03 8zM12 19.96c-.83-1.2-1.48-2.53-1.91-3.96h3.82A13.7 13.7 0 0112 19.96zM14.34 14H9.66a14.8 14.8 0 010-4h4.68a14.8 14.8 0 010 4zm.27 5.56c.6-1.11 1.06-2.31 1.38-3.56h2.95a8.03 8.03 0 01-4.33 3.56zM16.36 14a16.6 16.6 0 000-4h3.38a7.96 7.96 0 010 4h-3.38z" />
  </svg>
);
const LinkedIn = (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path fill="currentColor" d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 110-4.13 2.06 2.06 0 010 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.8 0 0 .77 0 1.73v20.54C0 23.22.8 24 1.77 24h20.45c.98 0 1.78-.78 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z" />
  </svg>
);
const Facebook = (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path fill="currentColor" d="M24 12.07C24 5.4 18.63 0 12 0S0 5.4 0 12.07c0 6.02 4.39 11.01 10.13 11.93v-8.44H7.08v-3.49h3.05V9.41c0-3.02 1.79-4.69 4.53-4.69 1.31 0 2.69.24 2.69.24v2.97h-1.52c-1.49 0-1.96.93-1.96 1.89v2.25h3.33l-.53 3.49h-2.8V24C19.61 23.08 24 18.09 24 12.07z" />
  </svg>
);
const Mail = (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path fill="currentColor" d="M3 4h18c.55 0 1 .45 1 1v14c0 .55-.45 1-1 1H3c-.55 0-1-.45-1-1V5c0-.55.45-1 1-1zm9 8.69l8-5.34V6l-8 5.34L4 6v1.35l8 5.34z" />
  </svg>
);

export function AuthorSocials({ bio }: { bio?: AuthorBio }) {
  if (!bio) return null;
  const links: { label: string; href: string; icon: ReactNode }[] = [];
  if (bio.orcid) links.push({ label: "ORCID profile", href: bio.orcid, icon: Orcid });
  if (bio.website) links.push({ label: "Website", href: bio.website, icon: Globe });
  if (bio.linkedin) links.push({ label: "LinkedIn", href: bio.linkedin, icon: LinkedIn });
  if (bio.facebook) links.push({ label: "Facebook", href: bio.facebook, icon: Facebook });
  if (bio.email) links.push({ label: `Email ${bio.email}`, href: `mailto:${bio.email}`, icon: Mail });
  if (!links.length) return null;

  return (
    <div className="author-socials">
      {links.map(({ label, href, icon }) => {
        const ext = !href.startsWith("mailto:");
        return (
          <a
            key={label}
            className="author-socials__link"
            href={href}
            aria-label={label}
            title={label}
            {...(ext ? { target: "_blank", rel: "noopener noreferrer" } : {})}
          >
            {icon}
          </a>
        );
      })}
    </div>
  );
}
