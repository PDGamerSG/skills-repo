#!/usr/bin/env python3
"""Plan custom hostnames and conservatively verify a deployed release."""
import argparse
from html.parser import HTMLParser
import json
import os
import re
import sys
import time
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z")
RESERVED = {"www", "mail", "api", "@", "*"}


def plan(project_name, domain="pallabdas.me", slug=None):
    if not project_name.strip():
        raise ValueError("Provide a nonempty --project-name.")
    if slug is None:
        ascii_name = unicodedata.normalize("NFKD", project_name).encode("ascii", "ignore").decode()
        slug = re.sub(r"[^a-z0-9]", "", ascii_name.lower())
    if not LABEL.fullmatch(slug) or slug in RESERVED:
        raise ValueError("Choose --slug with 1–63 lowercase ASCII letters/digits and internal hyphens; "
                         "reserved labels www, mail, and api are not allowed.")
    if (len(domain) > 253 or len(domain.split(".")) < 2
            or not all(LABEL.fullmatch(label) for label in domain.split("."))
            or domain.split(".")[-1].isdigit() or len(slug + "." + domain) > 253):
        raise ValueError("Use --domain as a lowercase DNS base domain such as pallabdas.me, without a URL or path.")
    hostname = slug + "." + domain
    return {"project_name": project_name, "slug": slug, "hostname": hostname,
            "url": "https://" + hostname}


def validate_url(url, require_https=True):
    parts = urlsplit(url)
    if (parts.scheme not in ({"https"} if require_https else {"http", "https"})
            or not parts.hostname or parts.username is not None or parts.password is not None
            or parts.fragment or re.search(r"[\s\x00-\x1f]", url)):
        raise ValueError("Provide an HTTPS URL with a hostname, without credentials or a fragment.")
    try:
        parts.port
    except ValueError as exc:
        raise ValueError("Use a valid HTTPS URL port.") from exc
    return parts


class SameHostRedirect(HTTPRedirectHandler):
    def __init__(self, url, require_https=True):
        self.origin = validate_url(url, require_https)
        self.require_https = require_https

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = validate_url(newurl, self.require_https)
        if ((target.hostname, target.port, target.scheme)
                != (self.origin.hostname, self.origin.port, self.origin.scheme)):
            raise ValueError("Blocked redirect outside the exact requested host/scheme/port: " + newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_page(url, *, require_https=True, timeout=8, max_bytes=2 * 1024 * 1024):
    """Fetch once with validated TLS; HTTP opt-out exists only for local transport tests."""
    validate_url(url, require_https)
    opener = build_opener(SameHostRedirect(url, require_https))
    deadline = time.monotonic() + timeout
    try:
        request = Request(url, headers={"User-Agent": "deploy-check/1.0", "Accept": "text/html"})
        with opener.open(request, timeout=timeout) as response:
            if response.status != 200:
                raise ValueError("Expected HTTP 200, received HTTP %s." % response.status)
            if response.headers.get_content_type() not in {"text/html", "application/xhtml+xml"}:
                raise ValueError("Expected an HTML page; received " + response.headers.get_content_type())
            body = bytearray()
            while True:
                if time.monotonic() > deadline:
                    raise ValueError("HTTP request exceeded its time limit.")
                chunk = response.read1(min(65536, max_bytes + 1 - len(body)))
                if not chunk:
                    break
                body.extend(chunk)
                if len(body) > max_bytes:
                    raise ValueError("HTML response body exceeds the size limit.")
            return body.decode(response.headers.get_content_charset() or "utf-8", errors="replace")
    except HTTPError as exc:
        exc.close()
        raise ValueError("Cannot fetch %s: HTTP %s; protected pages cannot establish freshness." % (url, exc.code)) from exc
    except (URLError, OSError, LookupError) as exc:
        raise ValueError("Cannot fetch %s: %s" % (url, exc)) from exc


def versioned_asset(asset):
    """Recognize an 8–64 hex path token or a named release query identifier of 8+ characters."""
    parts = urlsplit(asset)
    return bool(re.search(r"(?:^|[/_.-])[a-f0-9]{8,64}(?=[/_.-]|$)", parts.path, re.I) or any(
        key.lower() in {"v", "version", "build", "release", "hash", "dpl"}
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{7,127}", value) and re.search(r"\d", value)
        for key, value in parse_qsl(parts.query)))


def origin(parts):
    return parts.scheme, parts.hostname, parts.port or (443 if parts.scheme == "https" else 80)


class PageParser(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, url):
        super().__init__(convert_charrefs=True)
        self.url, self.stack, self.text, self.assets = url, [], [], set()
        self.versioned_assets = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        source = (attrs.get("src") if tag == "script" and (attrs.get("type") or "").lower()
                  in {"", "module", "text/javascript", "application/javascript"} else None)
        if tag == "link" and "stylesheet" in (attrs.get("rel") or "").lower().split():
            source = attrs.get("href")
        if source:
            parts = urlsplit(urljoin(self.url, source))
            if parts.scheme in {"https", "http"} and parts.path:
                asset = parts.path + ("?" + parts.query if parts.query else "")
                self.assets.add(asset)
                if origin(parts) == origin(urlsplit(self.url)) and versioned_asset(asset):
                    self.versioned_assets.add(asset)
        hidden = (bool(self.stack and self.stack[-1][1]) or tag in {"script", "style", "head", "template", "noscript"}
                  or "hidden" in attrs or attrs.get("aria-hidden") == "true"
                  or bool(re.search(r"(?:display\s*:\s*none|visibility\s*:\s*hidden)", attrs.get("style") or "", re.I)))
        if tag not in self.VOID:
            self.stack.append((tag, hidden))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if not self.stack or not self.stack[-1][1]:
            self.text.append(data)


def parse_page(html, url):
    parser = PageParser(url)
    parser.feed(html)
    return {"text": " ".join(" ".join(parser.text).split()), "assets": sorted(parser.assets),
            "versioned_assets": parser.versioned_assets}


BAD_PAGE = re.compile(r"DEPLOYMENT_(?:NOT_FOUND|DISABLED|BLOCKED)|404:\s*NOT_FOUND|"
                      r"deployment could not be found|Authentication Required|"
                      r"Vercel Security Checkpoint|Create Next App", re.I)


def evaluate(html, url, *, deployment_html=None, deployment_url=None, expect_text=(), expect_assets=()):
    page = parse_page(html, url)
    result = {"status": "pending", "url": url, "deployment_url": deployment_url,
              "evidence": [], "assets": page["assets"], "errors": []}
    errors, evidence = result["errors"], result["evidence"]
    if BAD_PAGE.search(page["text"]):
        errors.append("Custom URL displays a known error, protection screen, or starter placeholder.")
    for text in expect_text:
        if not text.strip():
            raise ValueError("Use --expect-text with nonempty, release-unique visible text.")
        if " ".join(text.split()) not in page["text"]:
            errors.append("Expected visible release text is missing: " + text)
    if expect_text and all(" ".join(text.split()) in page["text"] for text in expect_text):
        evidence.append("expected_text")
    for asset in expect_assets:
        if not asset.startswith("/") or asset.startswith("//") or "#" in asset:
            raise ValueError("Use --expect-asset as an exact asset pathname plus optional query, starting with /.")
        if asset not in page["assets"]:
            errors.append("Expected release asset is missing: " + asset)
    if expect_assets and all(asset in page["assets"] for asset in expect_assets):
        evidence.append("expected_assets")
    if deployment_url is not None:
        if deployment_html is None:
            errors.append("Deployment comparison page is unavailable; freshness remains pending.")
        else:
            baseline = parse_page(deployment_html, deployment_url)
            if BAD_PAGE.search(baseline["text"]):
                errors.append("Deployment comparison shows an error, protection screen, or starter placeholder.")
            if any(" ".join(text.split()) not in baseline["text"] for text in expect_text):
                errors.append("Expected visible release text is missing from the deployment comparison page.")
            if page["assets"] != baseline["assets"]:
                errors.append("Custom/deployment JS/CSS asset pathname+query sets differ (including missing/extra assets).")
            elif page["versioned_assets"] & baseline["versioned_assets"]:
                evidence.append("deployment_assets")
    if not evidence:
        errors.append("No freshness proof: supply release-unique --expect-text/--expect-asset or a deployment URL "
                      "with matching versioned same-origin JS/CSS assets. Stable/external assets alone are insufficient.")
    if not errors:
        result["status"] = "verified"
    return result


def verify(url, *, deployment_url=None, expect_text=(), expect_assets=(), fetcher=fetch_page):
    validate_url(url)
    if deployment_url:
        validate_url(deployment_url)
    try:
        html = fetcher(url)
        baseline = fetcher(deployment_url) if deployment_url else None
    except ValueError as exc:
        return {"status": "pending", "url": url, "deployment_url": deployment_url,
                "evidence": [], "assets": [], "errors": [str(exc)]}
    return evaluate(html, url, deployment_html=baseline, deployment_url=deployment_url,
                    expect_text=expect_text, expect_assets=expect_assets)


class JSONParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


def main(argv=None):
    parser = JSONParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    planner = commands.add_parser("plan")
    planner.add_argument("--project-name", required=True)
    planner.add_argument("--domain", default=os.environ.get("NAMECHEAP_BASE_DOMAIN", "pallabdas.me"),
                         help="Base domain (default: NAMECHEAP_BASE_DOMAIN, otherwise pallabdas.me).")
    planner.add_argument("--slug")
    verifier = commands.add_parser("verify", epilog="Asset comparison requires exact sets and a same-origin "
        "asset with an 8–64 hex path token or an 8+ character v/version/build/release/hash/dpl query ID containing "
        "a digit. Stable/external assets require an explicit release-unique text or asset expectation.")
    verifier.add_argument("--url", required=True)
    verifier.add_argument("--deployment-url")
    verifier.add_argument("--expect-text", action="append", default=[])
    verifier.add_argument("--expect-asset", action="append", default=[])
    try:
        args = parser.parse_args(argv)
        if args.command == "plan":
            result, code = plan(args.project_name, args.domain, args.slug), 0
        else:
            result = verify(args.url, deployment_url=args.deployment_url,
                            expect_text=args.expect_text, expect_assets=args.expect_asset)
            code = 0 if result["status"] == "verified" else 1
    except ValueError as exc:
        result, code = {"status": "error", "errors": [str(exc)]}, 2
    print(json.dumps(result))
    return code


if __name__ == "__main__":
    sys.exit(main())
