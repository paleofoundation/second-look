  // Research-feed summaries get the cosmetic account-wall (AccessGate blurs + overlays
  // [data-gated]) — but ONLY for logged-out visitors, decided server-side (the client can't
  // read the httpOnly session cookie to unlock it). Signed-in readers get no gate at all.
  if (type === "research-feed" && !loggedIn) {
    content = content.replace(/(<div[^>]*\bresearch-content__center\b[^>]*)>/, '$1 data-gated="research-feed">');
  }

  // Right-rail "Join the Roundtable" CTA: relabel the captured /auth/signup link to "Join the Waitlist".
  content = content
    .replace(/Yes,\s*I want to\s*(<a href="\/auth\/signup)/i, "$1")
    .replace(/(<a href="\/auth\/signup\/"[^>]*>)[\s\S]*?(<\/a>)/, "$1Join the Waitlist$2 and help shape the future of microbiome medicine.");

  return (
    <>
      <div dangerouslySetInnerHTML={{ __html: content }} />
