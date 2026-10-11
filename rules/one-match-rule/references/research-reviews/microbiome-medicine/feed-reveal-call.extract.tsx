  // Signed-in readers get the real Research Feed cards (excerpt + summary + Open/Link/Email)
  // in place of the "create a free account" teaser walls; logged-out readers keep the wall.
  const loggedIn = await isLoggedIn();
  if (loggedIn) content = await revealResearchFeedWalls(content);
