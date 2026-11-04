# Pending workflows

`evidence-gate.yml` and `deploy-cloudflare.yml` were moved into `.github/workflows/` on 2026-11-04. This note stays so the earlier staging location remains findable.

- `.github/workflows/evidence-gate.yml`: governance (which includes the citation gate) on every pull request; squash-merges page PRs (label `evidence-fill`, branch `fill/*` or `claude/remaprx-fill-*`) when green, then dispatches the deploy. It uses `GITHUB_TOKEN` only.
- `.github/workflows/deploy-cloudflare.yml`: build and `wrangler deploy` on push to main. The deploy steps are skipped until secrets `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` and variable `REMAPRX_D1_DATABASE_ID` exist, so missing credentials do not fail the workflow. `REMAPRX_CUSTOM_DOMAIN=remaprx.com` attaches the domain (cutover).
