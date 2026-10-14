# RemapRx custom domain

## Scope and hosting identity

Source: owner's 11 October 2026 request to finish connecting `remaprx.com` after saving the GoDaddy records. Preserve the existing nameservers and leave `www` unchanged. The request authorizes hosting-side verification of the existing apex mapping, with exact DNS instructions if more records are required.

- Sites project: `appgprj_6ac734459a508191a425263c7645a0be`
- Custom domain: `appgdom_6acb4adea5a08191997696dc913b9c0c`
- Hostname: `remaprx.com`
- Existing generated origin: `https://second-look-evidence.kmfp.chatgpt.site`
- Audience: public; unchanged by domain activation.

## DNS records preserved

These existing public records were independently confirmed during activation. They are DNS validation values, not application secrets.

| Type | GoDaddy host | Value |
| --- | --- | --- |
| A | @ | `162.159.143.30` |
| A | @ | `172.66.3.26` |
| TXT | _openai-site-verification | `openai-site-verification=as2bVr7DLvMZtVAb4agyU-M46hHSLVMbNrSP2JK-6UE` |
| TXT | _cf-custom-hostname | `931fe481-efe8-437c-91d5-940815e58ad5` |

No additional DNS record was required. No changes were made to DNS, nameservers or `www`.

## Activation and verification receipt — 11 October 2026

The native Sites `refresh_custom_domain_status` operation was run against the existing project and custom-domain IDs. At 13:39:43 UTC, SSL was `active` while the provider was `active_redeploying`. An interim HTTPS response returned the Sites dispatch 404 “No site here.”

The subsequent refresh, timestamped 13:40:27 UTC (16:40:27 Asia/Nicosia), returned:

- `status: active`
- `provider_status: active`
- `ssl_status: active`
- `last_error: null`

The browser then loaded `https://remaprx.com/` with the existing Second Look homepage, heading “A familiar drug. A different question.” and working rendered navigation. A separate HTTPS request returned HTTP 200 with `ssl_verify_result: 0`, using normal certificate validation. The certificate covers `remaprx.com`, is issued by Google Trust Services WE1, and is valid from 11 October 2026 12:38:14 UTC through 9 January 2027 13:38:10 UTC.

This was a hosting-only activation of the existing publication. No new source version was saved or deployed by this task; the latest saved version remained 23, commit `29166f85abbb12a2ff53f0cd3b77dcfdc9615b95`. The automatic hostname mapping rollout completed. The activation receipt does not assert scientific approval, a rebrand of the application, or verification of every application flow. No domain-connection work remained at completion.


## www repair — October 12, 2026

Source: owner reported the site appeared down and requested “Can you fix it?” after the apex returned HTTP 200 and `www` failed TLS. This expands the original apex-only scope to repair `www`, preserving nameservers and the existing public publication.

Registered `www.remaprx.com` on the same Sites project. Custom-domain ID: `appgdom_6acce4c428bc8191a92e0ef8aea302c8`. Public DNS at diagnosis had `CNAME www → remaprx.com.`; the apex retains both existing proxy A records. Sites supplies `custom-domains.chatgpt.site.` as the direct subdomain CNAME target.

At 13:47:56 UTC (16:47:56 Asia/Nicosia), the hosting refresh returned `status: pending`, `provider_status: active`, `ssl_status: active`, `last_error: null`. Certificate issuance completed, but Sites ownership verification remains pending. GoDaddy opened at its signed-out login screen; user sign-in requested before DNS editing. No DNS changes or new source publication have been made by this repair.

Required GoDaddy verification record:

| Type | GoDaddy host | Value |
| --- | --- | --- |
| TXT | _openai-site-verification.www | `openai-site-verification=NBmDwntFGsOIaLViE_p_cYD7Gb5FcNVa9BQxX46CMhg` |

The initial registration also returned `_cf-custom-hostname.www` TXT `a9614c1d-82b1-4baa-bd01-57095df0af86`; subsequent refreshes omit it and report provider/SSL active. Do not treat that initial record as a current outstanding requirement without rechecking. Next: add the current verification TXT, refresh Sites status, and verify HTTPS response at both hostnames. No redirect has been configured or verified.


### Completed repair receipt — October 12, 2026

Owner signed into regular Chrome and explicitly requested completion. Added only the required `_openai-site-verification.www` TXT record through GoDaddy. GoDaddy confirmed success, and its record list plus public Google DNS confirmed the exact value above, with TTL 3600. Preserved the existing `www → remaprx.com.` CNAME, apex A records and nameservers (`ns67.domaincontrol.com`, `ns68.domaincontrol.com`). No additional Cloudflare TXT was required.

Sites refresh at 13:54:39 UTC (16:54:39 Asia/Nicosia) returned `status: active`, `provider_status: active`, `ssl_status: active`, `last_error: null`. A normal certificate-validating HTTPS request returned HTTP 200 and title “RemapRx — The drug repurposing atlas.” Regular Chrome rendered the live homepage. The HTTP entry point returned 302 to `https://www.remaprx.com/`, and following it returned HTTP 200 with `ssl_verify_result: 0`. The apex separately returned HTTP 200 with certificate validation. Restricted-shell DNS/connectivity errors were resolved by verification outside the network sandbox; no TLS bypass was used.

The www repair is complete. It serves the same existing public application; no www-to-apex redirect was added. No application source version was saved or deployed by this repair. Concurrent site publication changed the current homepage title/identity independently, and this operation preserved it. Governance validation passed for the documentation. No remaining domain activation work is required.
