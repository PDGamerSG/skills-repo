---
name: namecheap
description: Connect a Vercel project to a Namecheap subdomain, reusing a ready release and saved account access. Use when the user invokes Namecheap or requests a custom URL, especially under pallabdas.me.
---

# Namecheap

Connect the requested hostname to the intended Vercel production release, verify it, and return the URL promptly.

## Reuse context and the ready release

Reuse the project, Vercel account/team, intended source revision, hostname, and authorization already established in the conversation. Ask only for information that remains ambiguous after focused discovery. Do not ask for a project name already supplied or infer a project from an unrelated working directory.

An explicit hostname wins. Otherwise use `NAMECHEAP_BASE_DOMAIN`, falling back to `pallabdas.me`; derive a label only when needed:

```sh
python3 <skill-dir>/scripts/deploy_check.py plan --project-name 'Agent Verse'
```

**Reuse the intended READY production deployment.** Build/deploy only if publishing is requested or the requested source is missing from that release. Preserve preview-only and read-only scope. A domain-only request covers DNS, project-domain assignment, TLS, and configuration that actually depends on the new origin. Keep unrelated CI repairs, application audits, dependency upgrades, test campaigns, and commits out of that task; report unrelated findings separately.

## Connect with minimal round trips

Use [references/deployment.md](references/deployment.md) for provider commands and access details.

1. Batch independent reads of the project, production deployment, hostname assignment, and authoritative DNS. Reuse correct existing settings. Obtain a replacement decision before disrupting another site's conflicting assignment or record, unless the user already authorized that replacement.
2. Reuse an authenticated browser session. Open Namecheap Advanced DNS directly at `https://ap.www.namecheap.com/Domains/DomainControlPanel/BASE_DOMAIN/advancedns`. Read saved credentials only if login is needed. Use one browser task/session and inspect the relevant records/form; avoid repeated full-page dumps or retries of a failed transport.
3. Attach with the explicit project: `vercel domains add HOST PROJECT --scope TEAM`. Then run `vercel domains verify HOST --scope TEAM` to obtain **this project's recommended CNAME**. Recommendations obtained before attachment can be generic. Quote API endpoints containing `?` or `&` in zsh.
4. Save the requested CNAME with Automatic TTL, read back the persisted row, and preserve other records. Record the save time. If the user changes the requested hostname, switch immediately and remove only task-created unused aliases using the exact project-domain scope.
5. Apply an origin allowlist update only when a direct cross-origin API/stream needs it. Preserve existing origins and service configuration; reuse the running backend image. Perform an independent rollout alongside DNS checks. Same-origin proxy requests need no CORS update.

## Bound verification and handle cached DNS

Use [references/verification.md](references/verification.md) for release comparison and fallback commands.

**Use one monotonic 180-second propagation deadline starting at DNS save.** All DNS, certificate, provider, and browser retries share it, including time spent on other work; waits are at most 30 seconds. Do not restart the clock after switching tools. Stop polling when the state is known or the deadline expires. Authentication or ownership blockers need an actionable status, not repeated retries.

Compare the custom page with the actual immutable production release. Local `dist/` can contain development overrides. If that deployment is protected, fetch its HTML once through authenticated `vercel curl`; keep protection enabled and secrets private. Vite hashes may not match the helper's automatic hex-hash detection: pass an explicit `--expect-asset` from production HTML or use its existing `parse_page`/`evaluate` functions for captured HTML.

If authoritative/public DNS and Vercel verification are correct but the OS/browser caches NXDOMAIN, use `curl --resolve` with a freshly verified public IP, the requested hostname/SNI, and normal certificate validation. Verify release assets, return the URL, and mark the custom-host browser check pending. Do not loop browser reloads, change system DNS/hosts, disable TLS, or present an HTTP check as browser proof.

For a domain-only task, check the main route, one meaningful harmless interaction, relevant API/stream connectivity, and relevant console/network errors. Reuse recent evidence where applicable. A full browser suite or all-routes audit requires its own task scope.

Lead the final response with the clickable custom URL. Briefly include the unique deployment URL/revision, actual verification evidence, and any precise pending limitation. Distinguish a verified HTTPS release from a pending custom-host browser check; do not claim unperformed tests or guarantee propagation speed.

## Access boundaries

Credentials: `NAMECHEAP_CREDENTIALS_FILE`, default `~/.config/namecheap/credentials.env`, with `NAMECHEAP_USERNAME` and `NAMECHEAP_PASSWORD`. Keep them outside repositories and skills, with owner-only permissions. Never print them or put literals in tool arguments; read them inside the automation process or use secret references. Reuse saved access; request missing credentials or fresh MFA through private secret input.

Use Namecheap's API only if it is already configured. Its `dns.setHosts` operation replaces the whole zone; avoid it for a single-record addition. Domain purchases, nameserver changes, wildcard setup, and mail changes are outside an ordinary subdomain connection.
