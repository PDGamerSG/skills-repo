# Verify the custom URL efficiently

## One deadline for propagation

Start one monotonic 180-second deadline when the DNS record is saved. Provider checks, DNS/TLS retries, browser fallbacks, and time spent on other work all consume this same window. Set each operation's timeout to the remaining budget; waits are at most 30 seconds. Never restart the deadline because a new tool or check begins. Stop polling as soon as the state is known or the deadline expires, and return the URL with precise evidence/pending status.

If the record was already correct, verify once before considering retries. Authentication, ownership, and build failures need an actionable blocker; repeated unchanged requests do not fix them.

## DNS, HTTPS, and stale local caches

Read the persisted CNAME and Vercel verification status. Check resolution with bounded queries, substituting the requested hostname:

```sh
dig +time=2 +tries=1 +short CNAME HOST
dig +time=2 +tries=1 +short A HOST
```

If local lookup is stale, compare the authoritative nameserver with a public resolver once. Discover the authoritative server for the base domain if unknown:

```sh
dig +time=2 +tries=1 +short NS BASE_DOMAIN
dig +time=2 +tries=1 @AUTHORITATIVE_NS HOST CNAME +noall +answer
dig +time=2 +tries=1 @1.1.1.1 HOST A +noall +answer
```

Follow the CNAME chain when needed; an empty CNAME response alone does not prove failure. Query AAAA when IPv6 routing is relevant. Use Vercel's certificate/domain diagnostics for unresolved provider state.

When authoritative/public DNS and Vercel verification are correct but the OS or browser caches NXDOMAIN, stop repeating browser reloads. Use a freshly verified public A-record IP for an HTTPS check that retains the requested hostname/SNI and certificate validation:

```sh
curl --resolve HOST:443:PUBLIC_DNS_IP --fail --silent --show-error \
  --max-time 10 --output CUSTOM_HTML https://HOST/
```

Use a private temporary directory for captured HTML. Check the actual response, release assets, and relevant API route using the same hostname. Do not use `--insecure`, edit system DNS/hosts, or silently follow redirects to another host. This proves the requested HTTPS endpoint serves the release through that IP; **it does not prove the cached browser can load it**. Return the URL and label that browser check pending. If public DNS/provider verification remains wrong at the deadline, report that exact pending condition instead.

## Compare with the actual immutable release

Use the intended READY deployment's unique URL/ID and source revision from context or provider metadata. Compare the same route on both hosts. Do not use a moving alias or local `dist/` as the baseline: local output may contain development API overrides absent from production.

For a publicly accessible deployment:

```sh
python3 <skill-dir>/scripts/deploy_check.py verify \
  --url https://HOST/ \
  --deployment-url https://UNIQUE_DEPLOYMENT.vercel.app/ \
  --expect-asset '/assets/ACTUAL_PRODUCTION_HASH.js'
```

Read the exact asset from actual release HTML; do not invent the filename. The helper automatically recognizes hex hash tokens, while Vite hashes can contain other characters. Use explicit `--expect-asset` for those builds; an unrecognized hash is not a reason to redeploy or modify the app. A real release-specific visible marker can use `--expect-text`. Shared titles, stable filenames, and HTTP 200 alone do not prove freshness.

For a protected immutable deployment, fetch the comparison HTML once using authorized CLI access:

```sh
vercel curl / --deployment DEPLOYMENT_ID -- \
  --fail --silent --show-error --max-time 15 --output BASELINE_HTML
```

Keep temporary files private. Do not disable protection, expose bypass tokens, or pass a protection/login page as the expected release. Avoid repeatedly calling the unauthenticated helper against a protected URL. For HTML already captured by authenticated CLI or `curl --resolve`, reuse `scripts/deploy_check.py`'s `parse_page` and `evaluate` functions locally: compare exact nonempty JS/CSS asset sets and supply an explicit current `expect_assets` entry from the baseline when automatic hash recognition does not apply. No helper rewrite is needed for this fallback. Inspect requested assets for relevant loading errors; static pages without assets need a release-specific marker or equivalent trusted content comparison.

The helper keeps TLS verification enabled and rejects known error/placeholder pages, cross-host redirects, missing expected content, missing/extra assets, and an unavailable baseline. Preserve those checks in a fallback. If comparison cannot be established, report freshness pending rather than guessing.

## Proportional browser smoke check

For a domain-only request, open the custom URL, verify the main route, exercise one meaningful harmless interaction, and inspect relevant console/network errors plus API/stream connectivity. Reuse recent application QA instead of rerunning every route or the full browser suite. If browser resolution is cached, retain recent functional evidence from the intended release and state that the custom-host browser check remains pending.

Check origin-dependent URLs or auth callbacks only when the domain change affects them. Use existing test accounts and non-destructive interactions. Do not create orders, send messages, or mutate unrelated live data as smoke checks. A screenshot alone does not prove release freshness.

## Focused remedies and final response

- Old release: inspect the exact domain-to-project assignment and intended production alias; check relevant caching/service-worker evidence before changing anything. Redeploy only if the intended source is absent or a new release is requested.
- API/stream origin rejection: apply the minimal allowlist change described in [deployment.md](deployment.md), preserving service configuration.
- Record/ownership conflict: preserve the other site pending the user's replacement decision, unless already authorized.
- Authentication, TLS, unresolved propagation, or browser-tool failure: state the specific incomplete check and next action; do not start an unrelated repair campaign.

Lead with the clickable custom URL, then briefly give the unique deployment URL/revision and DNS/TLS/release evidence. Name the route/interaction actually checked and any remaining limitation. Distinguish a valid HTTPS release from browser verification pending due to local NXDOMAIN. Do not claim unperformed checks or promise a guaranteed completion time dependent on authentication and external caches.
