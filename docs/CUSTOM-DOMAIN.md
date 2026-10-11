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
