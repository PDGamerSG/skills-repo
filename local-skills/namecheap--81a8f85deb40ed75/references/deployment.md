# Deployment and DNS

## Choose the shortest authorized path

Reuse the known project/team, hostname, revision, and intended READY production deployment. Inspect `.vercel/project.json` or provider metadata when context is insufficient; do not repeat repository discovery or build checks merely to connect a hostname. Batch independent account, project, domain, and DNS reads. Record the unique deployment URL and revision from trusted metadata; disclose included local changes when relevant.

Deploy only if the user requests publication or the intended source is not deployed. Then inspect applicable project instructions, run required release checks, link the exact project, deploy the intended source, and wait for READY. Do not auto-commit, repair unrelated CI, or broaden domain work into application QA. Preserve read-only/preview scope.

## Saved access and browser efficiency

The base domain defaults to `NAMECHEAP_BASE_DOMAIN` or `pallabdas.me`; an explicit user hostname/domain overrides both.

Reuse an authenticated Namecheap session before reading credentials. When login is actually needed, use `NAMECHEAP_CREDENTIALS_FILE` or `~/.config/namecheap/credentials.env`, containing `NAMECHEAP_USERNAME` and `NAMECHEAP_PASSWORD`. Check existence and variable names without displaying values. Keep the directory `0700` and file `0600` on POSIX, outside the project and skill. Never expose values in tool arguments, logs, snapshots, screenshots, or Git; do not enable shell tracing.

Use the active environment's supported browser and fallback rules. In T3 Code, call `preview_status` first. Keep one task/session, reuse working tabs, and avoid a transport already known to fail. A login in a separate profile does not authenticate the shared browser. Open the known domain's page directly:

```text
https://ap.www.namecheap.com/Domains/DomainControlPanel/BASE_DOMAIN/advancedns
```

Inspect the host-record table and current form. Batch known field actions and one save; use current snapshot references or semantic selectors. Raw CDP actions can invalidate snapshot references, so take a fresh relevant snapshot before reusing them. Avoid repeatedly retrieving navigation/footer content.

Read credentials inside the automation process, rather than returning them to the assistant. For a process with local file access:

```js
const { execFileSync } = await import('node:child_process');
const file = process.env.NAMECHEAP_CREDENTIALS_FILE ||
  `${(await import('node:os')).homedir()}/.config/namecheap/credentials.env`;
const credentials = JSON.parse(execFileSync('python3', ['-c',
  "import json,shlex,sys; from pathlib import Path; " +
  "print(json.dumps(dict(x.split('=',1) for x in " +
  "shlex.split(Path(sys.argv[1]).read_text(), comments=True) if '=' in x)))", file], {encoding: 'utf8'}));
// Fill the observed login fields; never log or return credentials.
```

Some runtimes do not inherit shell environment variables. Resolve an override first and pass only the nonsecret file path, or use tool-supported secret references. Missing credentials and fresh MFA require private secret input (`request_secret` in T3 Code), or user completion of normal verification. Do not request saved credentials again or persist MFA codes. Save missing credentials only with authorization.

## Vercel commands

Prefer installed `vercel`; use `npx --yes vercel@latest` only if needed. Reuse the authenticated account or complete its normal login flow. Supply the exact team scope and project; placeholders below must be replaced from verified context.

Independent inspection:

```sh
vercel whoami
vercel project inspect PROJECT --scope TEAM
vercel inspect UNIQUE_DEPLOYMENT_URL --scope TEAM
vercel domains inspect HOST --scope TEAM
```

Only when a new production release is required, from the correctly linked source:

```sh
vercel deploy /absolute/path/to/source --prod --yes --scope TEAM
vercel inspect UNIQUE_DEPLOYMENT_URL --wait --timeout=3m --scope TEAM
```

A wait timeout does not mean READY. Use the unique intended release, not a moving alias or an old preview. Report relevant build/authentication blockers without an unrelated repair campaign.

After checking for conflicts, attach to the explicit project and get its recommendation:

```sh
vercel domains add HOST PROJECT --scope TEAM
vercel domains verify HOST --scope TEAM
```

The project argument is required even in a linked directory: omitting it can add a domain to the account without assigning it to the project. Reuse an already correct assignment. Obtain the CNAME recommendation **after attachment** from verification output or that project's domain configuration. Pre-attachment API responses can return a generic target. Do not guess a target from another project or the deployment URL. Quote API endpoint arguments containing `?` or `&` in zsh to avoid glob expansion.

If the user changes the requested hostname, use the new hostname immediately. Remove only unused aliases created during this task, via the exact project's domain operation; avoid account-wide removal and preserve pre-existing domains.

## Namecheap record

1. Confirm the authoritative nameservers use Namecheap DNS. If another provider is authoritative, report it and use that provider only with appropriate access and authorization; do not change nameservers.
2. Inspect the requested label and Vercel assignment before mutation. Reuse a correct CNAME. A conflicting A/AAAA/CNAME or another site's assignment needs the user's replacement decision unless already authorized.
3. Save one CNAME: Host = requested subdomain label, Value = the project's exact recommended DNS hostname, TTL = Automatic. Use no URL scheme/path/query. Read the persisted row and record the monotonic save time for the single shared 180-second propagation deadline.
4. Preserve all unrelated records. If ownership requires a TXT record, add exactly the provider-specified host/value and preserve existing TXT records. Verify the hostname in Vercel; read [verification.md](verification.md) for bounded checks.

Use the website by default. The API is appropriate only with existing API access, key, and allowed client IP; a website password is not an API key. `namecheap.domains.dns.setHosts` replaces the entire zone. Avoid it for a single record; if explicitly chosen, fetch and preserve the complete current record set. Do not buy domains or change nameservers, wildcard records, or mail configuration for this task.

## Origin-dependent services

Check whether the browser uses a same-origin proxy or calls a separate API/stream origin. A same-origin proxy needs no CORS change. For direct cross-origin access, add only the required new origin to the existing allowlist; preserve old origins, secrets, ports, image, and service settings. Reuse the running backend image instead of rebuilding unchanged code. Run an independent configuration rollout alongside DNS propagation, then check the relevant request/stream. Keep it within the same verification deadline; report any rollout still pending.

## Provider references

Consult current documentation only when observed behavior differs:

- [Vercel domains CLI](https://vercel.com/docs/cli/domains)
- [Vercel custom domains](https://vercel.com/docs/domains/working-with-domains/add-a-domain)
- [Namecheap subdomains](https://www.namecheap.com/support/knowledgebase/article.aspx/9776/2237/how-to-create-a-subdomain-for-my-domain/)
