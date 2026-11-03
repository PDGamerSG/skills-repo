# Deployment and DNS

## Local settings and credentials

The personal default is `pallabdas.me`. A user-supplied domain overrides it; otherwise read `NAMECHEAP_BASE_DOMAIN` from the process environment, falling back to the default.

`NAMECHEAP_CREDENTIALS_FILE` may override `~/.config/namecheap/credentials.env`. The saved shell-compatible environment file has `NAMECHEAP_USERNAME` and `NAMECHEAP_PASSWORD`; it is already configured on the owner's machine. Check existence and required variable names without displaying values. Credentials should have owner-only access (directory `0700`, file `0600` on POSIX). Do not copy them into `.env` in an application, the skill folder, a catalog, screenshots, logs, or Git. Do not enable shell tracing. A GitHub installation does not bring account access with it.

If credentials are absent, use the runtime's private secret request; in T3 Code this is `request_secret`. Save them to the private file only when authorized. Credentials already saved do not need to be requested again. Verification codes are separate, temporary inputs; use the private input and do not persist them with the password.

Use the browser supported by the active environment. In T3 Code, call `preview_status` first and follow the environment's browser rules. A working authenticated tab can be reused. If a browser fallback is permitted after failures, explain the tool error and follow that browser's skill. Login in a separate Chrome/Safari profile does not imply an authenticated shared browser.

For a browser automation process that can read local files, parse the saved file within that process, then pass values to the observed login fields. For example, this Node snippet obtains values without returning them to the assistant:

```js
const { execFileSync } = await import('node:child_process');
const file = process.env.NAMECHEAP_CREDENTIALS_FILE ||
  `${(await import('node:os')).homedir()}/.config/namecheap/credentials.env`;
const credentials = JSON.parse(execFileSync('python3', ['-c',
  "import json,shlex,sys; from pathlib import Path; " +
  "print(json.dumps(dict(x.split('=',1) for x in " +
  "shlex.split(Path(sys.argv[1]).read_text(), comments=True) if '=' in x)))", file], {encoding: 'utf8'}));
// Fill the username/password controls observed on namecheap.com.
// Do not log credentials or return them in snapshots/evaluation results.
```

Some browser runtimes do not inherit the calling shell's environment. Resolve an override before invoking them and pass only the nonsecret file path. If tools offer secret references, use those rather than inserting password literals into tool arguments. Use normal Namecheap sign-in; handle its email verification or 2FA without attempting to bypass it.

## Identify the intended source

Inspect project instructions, framework, package manager, recent changes, and existing `.vercel/project.json`. Check `git status --short` and `git rev-parse HEAD` when it is a Git checkout. Avoid opening or printing unrelated application environment files. Locate an existing Vercel project before creating a duplicate. Ask for a local folder or repository URL if the named project cannot be identified reliably. If only an existing deployment is requested, identify its owning project and current intended production release.

Record the latest changes to verify: relevant routes, visible text, a release marker, changed assets, and key interactions. A deployment from a dirty working tree includes changes beyond its HEAD commit; state that in the final report. Do not auto-commit application work merely to obtain a revision label.

## Vercel

Prefer the installed `vercel` CLI. If absent, an available Node setup can use `npx --yes vercel@latest` for the same commands. Check account access with `vercel whoami`. Use existing login or a securely supplied token. If login is needed, complete the normal interactive/device flow. A Namecheap password is not a Vercel token, and an anonymous preview deployment cannot manage the user's domain.

Example commands below use `vercel`; substitute the chosen runner consistently. Supply `--scope TEAM` when working in a team account.

```sh
vercel whoami
vercel project inspect VERIFIED_PROJECT --scope TEAM
# Run required local build/type/test checks in the intended source folder first.
vercel deploy /absolute/path/to/verified/source --prod --yes --scope TEAM
vercel inspect https://UNIQUE-PRODUCTION-DEPLOYMENT.vercel.app --wait --timeout=3m --scope TEAM
vercel domains inspect PROJECT_LABEL.pallabdas.me --scope TEAM
vercel domains add PROJECT_LABEL.pallabdas.me VERIFIED_PROJECT --scope TEAM
```

The names above are arguments to replace from discovery, not suggested project names. Link/create the correct project before a `--yes` deploy if the source has no Vercel link; otherwise the CLI may infer the wrong project. Inspect the unique URL returned by this deploy, not an old preview or moving alias. Read build errors and correct project-scoped issues; stop when a fix needs information or authorization that is missing. `inspect --wait` timeout (including exit 124) does not mean the deployment is ready.

Adding a domain requires the **project argument even inside a linked directory**. Current Vercel behavior can add an apex domain only to the account if that argument is omitted. Get the recommended record for this exact project from its Domains panel, CLI diagnostics, or authenticated API; targets vary. Do not invent a target from a previous project, use the deployment's `vercel.app` address as a guessed target, or assume a generic Vercel CNAME is current.

## Namecheap record

1. Open **Domain List → Manage** for the chosen base domain, then **Advanced DNS**. Confirm Namecheap is actually the authoritative DNS manager; if another provider is authoritative, changing this page will not connect the site. Explain the real provider and continue there only with appropriate access and authorization.
2. Read the current host records before editing. For `agentverse.pallabdas.me`, Host is `agentverse`, not the full URL. Reuse the same CNAME if already correct. An existing conflicting CNAME/A/AAAA record or another Vercel project assignment needs a specific replacement decision before disrupting its site.
3. Add **CNAME Record**, Host = project label, Value = exact Vercel-provided DNS hostname (no `https://`, path, or query), TTL = **Automatic**. Save and read the persisted row. Keep other records intact; adding a CNAME is not a URL redirect.
4. Recheck the exact hostname in Vercel. If domain ownership requires a TXT record, add exactly the provider-specified host/value, preserving other records. Do not remove unrelated verification TXT records.

The Namecheap website is the default because account credentials are already saved. Use its API only when API access, API key, and allowed client IP are configured. A website password is not an API key. `namecheap.domains.dns.setHosts` replaces the whole record set: obtain and preserve all current records when that API is explicitly chosen. Do not replace the full zone merely to add one CNAME.

No registration purchase, nameserver migration, wildcard setup, or email changes are needed for an ordinary subdomain.

## Provider references

Check current help if commands or DNS recommendations differ:

- [Vercel domains CLI](https://vercel.com/docs/cli/domains)
- [Vercel deployment inspection](https://vercel.com/docs/cli/inspect)
- [Vercel custom domains](https://vercel.com/docs/domains/working-with-domains/add-a-domain)
- [Namecheap: create a subdomain](https://www.namecheap.com/support/knowledgebase/article.aspx/9776/2237/how-to-create-a-subdomain-for-my-domain/)
