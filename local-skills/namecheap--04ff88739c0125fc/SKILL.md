---
name: namecheap
description: Use when the user invokes Namecheap or wants a Vercel project published on a Namecheap subdomain, especially a project under pallabdas.me.
---

# Namecheap

Publish the requested project to Vercel, connect its Namecheap subdomain, and verify that the custom URL shows the intended release and working features.

## Start with the project

If the invocation contains no project name, ask **“What is the project name?”** and wait. Reuse a name already supplied. Resolve its actual local folder, repository, or existing Vercel project; ask for its location only if discovery leaves ambiguity. An unrelated current directory is not the source.

Default domain: `pallabdas.me`, overridable by the user's request or `NAMECHEAP_BASE_DOMAIN`. Generate the hostname with the bundled helper:

```sh
python3 <skill-dir>/scripts/deploy_check.py plan --project-name 'Agent Verse'
```

This yields `https://agentverse.pallabdas.me`. Honor an explicit subdomain. Show the selected project and URL, then continue within the requested deployment scope.

## Authenticate and deploy

Read [references/deployment.md](references/deployment.md) for account access, exact CLI commands, and DNS editing.

Reuse `NAMECHEAP_CREDENTIALS_FILE`, defaulting to `~/.config/namecheap/credentials.env`. It contains `NAMECHEAP_USERNAME` and `NAMECHEAP_PASSWORD`. Read values directly into the browser automation process without printing them. Keep this file outside the project and skill; publish no credentials. Reuse saved values instead of requesting them again. If Namecheap requires a fresh verification code, use the environment's private secret input or let the user complete verification.

Use an authenticated Vercel account that can manage the project and domain. Confirm the correct team and source. Run project-required build checks, deploy the intended current source to **production**, and capture the unique deployment URL and source revision (including whether local changes were included). Honor an explicit preview-only or read-only request instead of making production changes. Wait for Vercel `READY`; a build failure or timeout is incomplete.

## Connect the hostname

Inspect the existing Vercel domain assignment and Namecheap records first. Reuse an already correct assignment. If the hostname serves another project or has conflicting records, resolve that specific conflict with the user before replacement.

Attach the hostname to the exact Vercel project, including its project name in `vercel domains add`. Obtain **that project's current recommended CNAME target** from Vercel. In Namecheap Advanced DNS, add the subdomain label as Host, the exact target as Value, and Automatic TTL. Preserve existing website, email, and unrelated records. Inspect the saved row and verify the domain in Vercel. Changing nameservers or buying a domain is outside this workflow.

## Verify the latest release

Read [references/verification.md](references/verification.md). Automatically check DNS, valid HTTPS, the final hostname, and freshness against the unique production deployment. Use the helper plus real browser checks of recently changed routes and important interactions. HTTP 200 alone does not establish that the latest work is live.

If the custom domain shows an older build, repair the alias or deployment within scope and recheck. Bound propagation checks to three minutes, with individual waits at most 30 seconds; report pending DNS/certificate work accurately if it takes longer. Stop on authentication, ownership, or build failures with the actionable blocker.

Finish with the clickable custom URL, Vercel deployment URL, verified source/build and feature checks, and any remaining limitation. Claim completion only when the intended release and tested features work on the custom URL.
