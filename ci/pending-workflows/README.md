# Pending workflows

These two files belong in `.github/workflows/`. They were committed here because the pushing token lacks GitHub's `workflow` scope. Move them with a token that has it (or the GitHub web UI):

    git mv ci/pending-workflows/evidence-gate.yml ci/pending-workflows/deploy-cloudflare.yml .github/workflows/

- evidence-gate.yml: governance (which now includes the citation gate) on every PR; squash-merges page PRs (label `evidence-fill`, branch `fill/*` or `claude/remaprx-fill-*`) when green, then dispatches the deploy.
- deploy-cloudflare.yml: build and `wrangler deploy` on push to main. Skips until secrets `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` and variable `REMAPRX_D1_DATABASE_ID` exist. `REMAPRX_CUSTOM_DOMAIN=remaprx.com` attaches the domain (cutover).
