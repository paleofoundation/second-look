import Link from "next/link";
import { notFound } from "next/navigation";
import { sectionBySegment, listByType, type ListItem } from "@/lib/content";
import { asciiSlug } from "@/lib/slugs";

export async function ArchiveView({ segment }: { segment: string; page?: number }) {
  const section = sectionBySegment(segment);
  if (!section) notFound();

  const { items, total } = await listByType(section.type, 1, 1000);

  // Group alphabetically by first letter (matches the original A–Z archive).
  const groups = new Map<string, ListItem[]>();
  for (const it of items) {
    const first = (it.title.trim()[0] || "#").toUpperCase();
    const key = /[A-Z]/.test(first) ? first : "#";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(it);
  }
  const letters = [...groups.keys()].sort();

  return (
    <div className="site-content flex">
      <main className="main">
        <div className="rgbc-hero">
          <div className="rgbc-hero__wrapper wrapper">
            <div className="rgbc-hero__center rgbc-hero__center--archive">
              <nav className="breadcrumb">
                <ol className="breadcrumb__wrapper">
                  <li className="breadcrumb__item">
                    <Link className="breadcrumb__link" href="/">Home</Link>
                  </li>
                  <li className="breadcrumb__item">
                    <span className="breadcrumb_last"><span className="badge">{section.label}</span></span>
                  </li>
                </ol>
              </nav>
              <div className="rgbc-hero__content">
                <h1 className="rgbc-hero__title">{section.label}</h1>
                <p>{section.blurb}</p>
              </div>
            </div>
          </div>
        </div>

        <section className="rgbc-content">
          <div className="rgbc-content__wrapper wrapper">
            <div className="rgbc-content__main rgbc-archive">
              <h2 className="rgbc-archive__title">{total} {section.label}</h2>
              <div className="rgbc-archive__letters">
                {letters.map((L) => (
                  <a key={L} className="rgbc-archive__item" href={`#letter-${L}`}>{L}</a>
                ))}
              </div>
              {letters.map((L) => (
                <div key={L}>
                  <div className="rgbc-archive__header" id={`letter-${L}`}>
                    <div className="rgbc-archive__letter">{L}</div>
                  </div>
                  {groups.get(L)!.map((it) => (
                    <div key={it.id} className="rgbc-archive__post">
                      <a className="rgbc-archive__link" href={`/${segment}/${asciiSlug(it.slug) || it.slug}`}>{it.title}</a>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
