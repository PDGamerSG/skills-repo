# Verify the custom URL

“All progress is shown” means that the intended current release reaches the custom domain and its relevant features work there. A DNS row or HTTP 200 does not prove release freshness or functional behavior.

## Establish expected results before checking

Capture the Vercel deployment ID/unique production URL and the source revision from this run. Read the actual recent changes to choose visible release-specific text, a release/build marker, or changed hashed assets. Identify the important routes and changed interactions to smoke-test. For an existing deployment, establish which production deployment the user intends before comparing it.

Do not change the app merely to insert a test marker unless it is needed and within scope. Do not use a moving `project.vercel.app` alias as the reference when the immutable deployment URL is available.

## DNS and HTTPS

Read the Namecheap saved CNAME and Vercel domain status. If `dig` is available:

```sh
dig +short CNAME agentverse.pallabdas.me
dig +short A agentverse.pallabdas.me
dig +short AAAA agentverse.pallabdas.me
```

Compare the returned CNAME with Vercel's exact recommended target. Query the authoritative nameserver as well if the local resolver is stale. Check domain verification and certificate status in Vercel. CNAME flattening or a cached resolver may need provider diagnostics; do not diagnose solely from an empty `dig CNAME` answer.

Run the helper against the real custom domain:

```sh
python3 <skill-dir>/scripts/deploy_check.py verify \
  --url https://agentverse.pallabdas.me \
  --deployment-url https://UNIQUE-PRODUCTION-DEPLOYMENT.vercel.app \
  --expect-text 'A visible feature unique to this release'
```

`--expect-text` and `--expect-asset` may be used as the helper's help permits. Choose actual release-specific values; a shared title like “Welcome” is not freshness evidence. For a page built from hashed JS/CSS, the helper can compare nonempty asset sets against the unique deployment page. Matching assets is supporting release evidence; use an explicit current marker/feature when the app has stable asset names. A static page with no assets needs a release-specific marker instead.

The helper emits JSON and fails conservatively on TLS/network errors, errors/placeholder pages, cross-host redirects, unavailable comparison deployments, missing expected content, mismatched builds, or absence of freshness evidence. Use default TLS verification. A redirect to another project's working site is not a successful custom URL. Follow redirects only to inspect and diagnose the actual outcome.

If deployment protection prevents comparing the unique URL, do not disable protection globally or publish a bypass secret. Use authorized authenticated inspection and a browser comparison plus an explicit release-specific marker on the public URL. Report the comparison limitation. Never report an inaccessible baseline comparison as passed.

## Functional checks in the browser

Use the environment's browser tools to open **the custom URL**. This is browser work explicitly included in a Namecheap deployment invocation. Inspect the homepage and routes touched by recent changes. Exercise at least one meaningful changed interaction and the project's main flow when feasible. Check browser console and failed network requests for relevant application errors. Verify loaded assets, links, API endpoints, and auth callbacks use the intended environment; a build that loads while its API fails is incomplete.

Use non-destructive interactions and existing test accounts. Report any authenticated or data-changing flow that could not be tested; do not invent successful tests. Do not create orders, send emails, or make unrelated live data mutations as smoke checks. A screenshot can help inspect the page but is not by itself proof of the release.

## Retries and fixes

Recheck changed conditions rather than redeploying blindly. Within a three-minute propagation window, keep individual waits at most 30 seconds and share meaningful updates. When the window expires, stop and return a precise pending status and next check; DNS/certificate propagation is not a completed verification.

- Old content: confirm domain→project assignment, the production deployment/alias, CDN caching, and service workers. Point the domain at the intended production release and retest within the user's scope.
- Build/runtime failure: inspect Vercel build/runtime logs and required environment settings without printing their values. Correct relevant configuration or report the blocker.
- Ownership/record collision: preserve the current site until the user decides whether to replace it or choose another label.
- Browser unavailable: report HTTP/DNS results and that feature verification remains incomplete.

## Final report

Return the clickable custom URL and unique Vercel deployment URL, source revision/local-change status, DNS/TLS/freshness results, and the routes/interactions actually tested. If anything is pending or untested, name it plainly. Do not promise that an unrelated future change will appear without another production deployment.
