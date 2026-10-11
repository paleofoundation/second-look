/* Native anchors preserve the shared search and access gate, which initialize on page load. */
/* eslint-disable @next/next/no-html-link-for-pages */
import Image from "next/image";
import styles from "./HomePage.module.css";
const cx = (names: string) => names.split(" ").map((name) => styles[name]).join(" ");

const collections = [
  {
    number: "01",
    eyebrow: "CONDITIONS",
    title: "Start with the clinical question",
    copy: "Explore condition-specific microbiome signatures and the evidence behind them.",
    path: "/conditions",
    links: [{"title": "Hashimoto’s Thyroiditis", "href": "/conditions/hashimotos-thyroiditis"}, {"title": "Crohn’s Disease", "href": "/conditions/crohns-disease"}, {"title": "Primary Ovarian Insufficiency", "href": "/conditions/primary-ovarian-insufficiency-poi"}],
  },
  {
    number: "02",
    eyebrow: "INTERVENTIONS",
    title: "Follow the evidence to action",
    copy: "Assess candidate interventions through both mechanistic and clinical evidence.",
    path: "/interventions",
    links: [{"title": "Cholestyramine", "href": "/interventions/cholestyramine"}, {"title": "Resistance Training", "href": "/interventions/resistance-strength-training"}, {"title": "Lactulose", "href": "/interventions/lactulose"}],
  },
  {
    number: "03",
    eyebrow: "CONCEPTS",
    title: "Understand the mechanism",
    copy: "Build a shared language for the biological pathways behind each signature.",
    path: "/definition",
    links: [{"title": "Metalloprotease", "href": "/definition/metalloprotease"}, {"title": "Ferroptosis", "href": "/definition/ferroptosis"}, {"title": "Estrogen", "href": "/definition/estrogen"}],
  },
];

const research = [
  {
    title: "Akkermansia muciniphila in infectious disease: a new target for this next-generation probiotic?",
    kind: "Microbe",
    href: "/research-feeds/akkermansia-muciniphila-in-infectious-disease-a-new-target-for-this-next-generation-probiotic",
  },
  {
    title: "Characterizing the gut microbiota in females with infertility",
    kind: "Research feed",
    href: "/research-feeds/characterizing-the-gut-microbiota-in-females-with-infertility-and-preliminary-results-of-a-water-soluble-dietary-fiber-intervention-study",
  },
  {
    title: "Fecal calprotectin biomarker in IBD: clinical use",
    kind: "Clinical concept",
    href: "/research-feeds/fecal-calprotectin-biomarker-in-ibd",
  },
];

function Search() {
  return (
    <form className={cx("search") + " js-search-form"}  action="/search" method="get" role="search">
      <label className={cx("sr-only")}  htmlFor="evidence-search">Search Microbiome Medicine</label>
      <input className="js-search-input" autoComplete="off" id="evidence-search" name="q" type="search" placeholder="What do you want to learn about?" required />
      <button type="submit" aria-label="Search"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true"><circle cx="10" cy="10" r="7" /><path d="m15 15 7 7" /></svg></button>
      <div className={cx("search-results") + " js-search-result"}  aria-live="polite" style={{ display: "none" }} />
    </form>
  );
}

export function HomePage() {
  return (
    <main className={styles.home} id="main-content">
      <section className={cx("hero")}  id="top">
        <div className={cx("hero__copy")} >

          <h1>Turning Microbiome Signatures into Validated Interventions.</h1>
          <p className={cx("hero__intro")} >
            We translate microbiome research into condition-specific signatures,
            mechanistic targets, and interventions validated by a logic-based,
            dual evidence framework.
          </p>
          <Search />
          <div className={cx("quick-searches")} >
            <span>Popular searches</span>
            <a href="/conditions/endometriosis">Endometriosis</a>
            <a href="/microbes/akkermansia-muciniphila">Akkermansia</a>
            <a href="/interventions/low-nickel-diet">Low-nickel diet</a>
          </div>
        </div>

        <div className={cx("hero__media")} >
          <div className={cx("image-frame")} >
            <Image
              src="/wp-content/uploads/2026/09/microbiome-evidence-researcher.webp"
              width={1448} height={1086} sizes="(max-width: 1023px) 100vw, 42vw" preload
              alt="A researcher mapping microbial colony patterns and evidence relationships"
            />
            <div className={cx("image-caption")} ><span>EVIDENCE MAPPING</span><strong>From observed pattern to clinical hypothesis</strong></div>
          </div>
          <div className={cx("evidence-note")} >
            <span className={cx("evidence-note__mark")} >MSCS</span>
            <p><strong>Evidence should be traceable.</strong><br />Every signature shows what supports it, and how confident we are.</p>
            <a href="#method" aria-label="Learn about the validation method">→</a>
          </div>
        </div>
      </section>

      <section className={cx("credibility")}  aria-label="Platform principles">
        <span>BUILT FOR CLINICIANS</span>
        <span>BACKED BY EVIDENCE</span>
        <span>DESIGNED TO CLOSE THE TRANSLATIONAL GAP</span>
      </section>

      <section className={cx("section")}  id="explore">
        <div className={cx("section-intro centered")} >

          <h2>One clinical question. <br />A connected evidence map.</h2>
          <p>Move between conditions, mechanisms, and interventions without losing the thread.</p>
        </div>

        <div className={cx("collection-grid")} >
          {collections.map((collection) => (
            <article className={cx("collection-card")}  key={collection.number}>
              <div className={cx("collection-card__top")} ><span>{collection.number}</span><small>{collection.eyebrow}</small></div>
              <h3>{collection.title}</h3>
              <p>{collection.copy}</p>
              <ul>
                {collection.links.map((link) => <li key={link.href}><a className="rgbc-archive__link" href={link.href}>{link.title}</a></li>)}
              </ul>
              <a href={collection.path} className={cx("card-link")} >See all</a>
            </article>
          ))}
        </div>
      </section>

      <section className={cx("method section")}  id="method">
        <div className={cx("method__heading")} >

          <h2>From observation <br />to clinical direction.</h2>
          <p>Not every association is an intervention. Our dual evidence framework separates what is observed, what is mechanistically plausible, and what is clinically supported.</p>
          <a href="/how-microbiome-signatures-are-derived" className={cx("text-link")} >How signatures are derived <span>→</span></a>
        </div>
        <ol className={cx("method__steps")} >
          <li><span>01</span><div><h3>Identify the signature</h3><p>Map reproducible microbial and metallomic patterns by condition.</p></div></li>
          <li><span>02</span><div><h3>Test the mechanism</h3><p>Connect each pattern to plausible biological targets and causal pathways.</p></div></li>
          <li><span>03</span><div><h3>Validate the intervention</h3><p>Weigh mechanistic and clinical evidence together, with uncertainty visible.</p></div></li>
        </ol>
      </section>

      <section className={cx("section")}  id="research">
        <div className={cx("research__head")} >
          <div><h2>Evidence, kept current.</h2></div>
          <a href="/research-feeds?mode=category" className={cx("outline-button")} >View all research <span>→</span></a>
        </div>
        <div className={cx("research-list") + " rgbc-content__details-content"} >
          {research.map((item) => (
            <a className={cx("research-row")}  href={item.href} key={item.title}>
              <p>{item.title}</p>
              <div className="rgbc-content__details-meta">
                <small className="rgbc-content__details-date">{item.kind}</small>
              </div>
            </a>
          ))}
        </div>
      </section>

      <section className={cx("membership section")}  id="membership">
        <div>

          <h2>Join the Frontlines of <br />Microbiome Consensus</h2>
          <p>Get early access to roundtable invitations, consensus-building updates, and the latest research shaping clinical practice.</p>
          <form className={cx("join")}  action="/api/subscribe" method="post">
            <label className={cx("sr-only")}  htmlFor="join-email">Your email address</label>
            <input id="join-email" name="email" type="email" placeholder="Your email address" required />
            <button type="submit">Let’s Shape the Future <span>→</span></button>
          </form>
        </div>
      </section>

    </main>
  );
}

