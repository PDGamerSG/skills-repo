import importlib.util
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "deploy_check.py"
spec = importlib.util.spec_from_file_location("deploy_check", SCRIPT)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)
CUSTOM = "https://agentverse.example.org"
DEPLOYMENT = "https://release-123.vercel.app"
CURRENT = '<h1>Release amber-2026</h1><script type="module" src="/app-8ef3c1a9.js?v=2"></script>'


class PlanCLITests(unittest.TestCase):
    def cli(self, *args, base_domain=None):
        environment = {key: value for key, value in os.environ.items() if key != "NAMECHEAP_BASE_DOMAIN"}
        if base_domain is not None:
            environment["NAMECHEAP_BASE_DOMAIN"] = base_domain
        return subprocess.run([sys.executable, str(SCRIPT), *args], text=True,
                              capture_output=True, timeout=5, env=environment)

    def test_default_plan_removes_spaces_and_ascii_punctuation(self):
        result = self.cli("plan", "--project-name", "Agent Verse")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {
            "project_name": "Agent Verse", "slug": "agentverse",
            "hostname": "agentverse.pallabdas.me",
            "url": "https://agentverse.pallabdas.me",
        })

    def test_explicit_slug_preserves_hyphens_and_domain_override(self):
        result = self.cli("plan", "--project-name", "Café: Deck!",
                          "--slug", "cafe-deck", "--domain", "example.org")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["url"], "https://cafe-deck.example.org")

    def test_base_domain_environment_default_and_explicit_override(self):
        result = self.cli("plan", "--project-name", "Agent Verse", base_domain="env.example.org")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["hostname"], "agentverse.env.example.org")
        result = self.cli("plan", "--project-name", "Agent Verse", "--domain", "explicit.example.org",
                          base_domain="env.example.org")
        self.assertEqual(json.loads(result.stdout)["hostname"], "agentverse.explicit.example.org")

    def test_unicode_default_slug_is_normalized_to_ascii(self):
        result = self.cli("plan", "--project-name", "Café: Déck!")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["slug"], "cafedeck")

    def test_cli_rejects_plain_http_and_returns_json(self):
        result = self.cli("verify", "--url", "http://127.0.0.1:1", "--expect-text", "release-123")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("HTTPS", " ".join(json.loads(result.stdout)["errors"]))

    def test_cli_reports_real_https_connection_failure_as_pending(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        result = self.cli("verify", "--url", "https://127.0.0.1:%s" % port,
                          "--expect-text", "Release amber-2026")
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pending")
        self.assertTrue(payload["errors"])

    def test_unsafe_slugs_and_domains_are_actionable_json_errors(self):
        for args in [
            ("--project-name", "!!!"),
            ("--project-name", "www"),
            ("--project-name", "mail"),
            ("--project-name", "api"),
            ("--project-name", "x" * 64),
            ("--project-name", "Project", "--slug", "bad_name"),
            ("--project-name", "Project", "--slug", "-bad"),
            ("--project-name", "Project", "--domain", "https://example.org"),
            ("--project-name", "Project", "--domain", "example..org"),
            ("--project-name", "Project", "--domain", "localhost"),
        ]:
            with self.subTest(args=args):
                result = self.cli("plan", *args)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stdout.startswith("{"), result.stderr)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "error")
                self.assertTrue(payload["errors"])


class EvidenceTests(unittest.TestCase):
    def evaluate(self, html=CURRENT, **kwargs):
        self.assertTrue(callable(getattr(check, "evaluate", None)), "missing evidence evaluator")
        return check.evaluate(html, CUSTOM, **kwargs)

    def test_visible_release_text_is_positive_evidence(self):
        result = self.evaluate(expect_text=["Release amber-2026"])
        self.assertEqual(result["status"], "verified")
        self.assertIn("expected_text", result["evidence"])

    def test_script_style_and_hidden_text_do_not_count_as_visible_text(self):
        for html in ['<script>"Release amber-2026"</script><h1>Old release</h1>',
                     '<style>/* Release amber-2026 */</style><h1>Old release</h1>',
                     '<div hidden>Release amber-2026</div><h1>Old release</h1>']:
            with self.subTest(html=html):
                self.assertEqual(self.evaluate(html, expect_text=["Release amber-2026"])["status"], "pending")

    def test_http_200_and_same_generic_text_are_not_freshness_evidence(self):
        result = self.evaluate("<h1>Welcome</h1>", deployment_html="<h1>Welcome</h1>",
                               deployment_url=DEPLOYMENT)
        self.assertEqual(result["status"], "pending")
        self.assertTrue(result["errors"])

    def test_own_origin_hashed_module_and_stylesheet_fingerprints_match(self):
        custom = '<script type="module" src="https://agentverse.example.org/_next/static/a-82af6c91.js?v=42"></script><link rel="stylesheet" href="/a.css?x=2">'
        baseline = '<script type="module" src="/_next/static/a-82af6c91.js?v=42"></script><link rel="stylesheet" href="https://release-123.vercel.app/a.css?x=2">'
        result = self.evaluate(custom, deployment_html=baseline, deployment_url=DEPLOYMENT)
        self.assertEqual(result["status"], "verified")
        self.assertEqual(result["assets"], ["/_next/static/a-82af6c91.js?v=42", "/a.css?x=2"])
        self.assertIn("deployment_assets", result["evidence"])

    def test_stable_assets_cannot_prove_freshness_when_visible_release_differs(self):
        old = '<h1>Old release</h1><script src="/app.js"></script>'
        new = '<h1>New release</h1><script src="/app.js"></script>'
        self.assertEqual(self.evaluate(old, deployment_html=new, deployment_url=DEPLOYMENT)["status"], "pending")
        self.assertEqual(self.evaluate(new, deployment_html=new, deployment_url=DEPLOYMENT,
                                       expect_text=["New release"])["status"], "verified")

    def test_external_assets_cannot_establish_freshness_even_with_a_hash(self):
        for source in ["https://cdn.example/tracker.js", "https://cdn.example/tracker-82af6c91.js"]:
            with self.subTest(source=source):
                html = '<h1>Welcome</h1><script src="' + source + '"></script>'
                self.assertEqual(self.evaluate(html, deployment_html=html,
                                              deployment_url=DEPLOYMENT)["status"], "pending")

    def test_versioned_asset_must_be_own_origin_on_both_pages(self):
        custom = '<script src="/app-82af6c91.js"></script>'
        external = '<script src="https://cdn.example/app-82af6c91.js"></script>'
        self.assertEqual(self.evaluate(custom, deployment_html=external, deployment_url=DEPLOYMENT)["status"], "pending")
        self.assertEqual(self.evaluate(external, deployment_html=custom, deployment_url=DEPLOYMENT)["status"], "pending")

    def test_recognizable_release_query_can_establish_freshness(self):
        for path in ["/app.js?release=amber-2026-a1", "/app.js?build=82af6c91"]:
            with self.subTest(path=path):
                html = '<script src="' + path + '"></script>'
                self.assertEqual(self.evaluate(html, deployment_html=html,
                                              deployment_url=DEPLOYMENT)["status"], "verified")
        for path in ["/app.js?v=1", "/app.js?utm=amber-2026-a1"]:
            with self.subTest(path=path):
                html = '<script src="' + path + '"></script>'
                self.assertEqual(self.evaluate(html, deployment_html=html,
                                              deployment_url=DEPLOYMENT)["status"], "pending")

    def test_old_content_missing_extra_and_changed_asset_query_fail(self):
        for html in [
            '<h1>Release amber-2026</h1><script src="/app-old.js?v=1"></script>',
            '<h1>Release amber-2026</h1>',
            CURRENT + '<script src="/extra.js"></script>',
            CURRENT.replace("?v=2", "?v=3"),
        ]:
            with self.subTest(html=html):
                result = self.evaluate(html, deployment_html=CURRENT, deployment_url=DEPLOYMENT,
                                       expect_text=["Release amber-2026"])
                self.assertEqual(result["status"], "pending")

    def test_all_explicit_expectations_must_match(self):
        self.assertEqual(self.evaluate(expect_text=["Release amber-2026", "missing"])["status"], "pending")
        self.assertEqual(self.evaluate(expect_assets=["/app-8ef3c1a9.js?v=2", "/missing.js"])["status"], "pending")
        self.assertEqual(self.evaluate(expect_assets=["/app-8ef3c1a9.js?v=2"])["status"], "verified")

    def test_empty_expected_text_and_non_path_asset_are_invalid(self):
        with self.assertRaisesRegex(ValueError, "nonempty"):
            self.evaluate(expect_text=[" "])
        with self.assertRaisesRegex(ValueError, "pathname"):
            self.evaluate(expect_assets=["https://other.example/app-new.js?v=2"])

    def test_missing_expectation_is_not_listed_as_positive_evidence(self):
        result = self.evaluate(expect_text=["missing-release"])
        self.assertNotIn("expected_text", result["evidence"])

    def test_non_javascript_script_type_does_not_prove_release(self):
        html = '<h1>Welcome</h1><script type="application/json" src="/info.json"></script>'
        self.assertEqual(self.evaluate(html, deployment_html=html,
                                      deployment_url=DEPLOYMENT)["status"], "pending")

    def test_expected_release_text_must_also_exist_on_requested_baseline(self):
        baseline = CURRENT.replace("Release amber-2026", "Old release")
        result = self.evaluate(deployment_html=baseline, deployment_url=DEPLOYMENT,
                               expect_text=["Release amber-2026"])
        self.assertEqual(result["status"], "pending")

    def test_expected_text_absent_from_old_page_fails_with_current_assets(self):
        old = CURRENT.replace("Release amber-2026", "Old release")
        self.assertEqual(self.evaluate(old, deployment_html=CURRENT, deployment_url=DEPLOYMENT,
                                       expect_text=["Release amber-2026"])["status"], "pending")

    def test_known_vercel_error_and_placeholder_cannot_verify(self):
        for text in ["DEPLOYMENT_NOT_FOUND", "The deployment could not be found on Vercel.",
                     "404: NOT_FOUND", "Authentication Required", "Create Next App"]:
            with self.subTest(text=text):
                result = self.evaluate("<h1>" + text + "</h1>", expect_text=[text])
                self.assertEqual(result["status"], "pending")


class FixtureHandler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        self.server.paths.append(self.path)
        if self.path == "/external":
            self.send_response(302)
            self.send_header("Location", "http://localhost:%s/current" % self.server.server_port)
            self.end_headers()
            return
        if self.path == "/same-host":
            self.send_response(302)
            self.send_header("Location", "/current")
            self.end_headers()
            return
        status = 401 if self.path == "/protected" else 200
        body = ("Authentication Required" if status == 401 else CURRENT).encode()
        if self.path == "/large":
            body = b"x" * 1000
        if self.path == "/trickle":
            body = b"abcdefghij"
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            if self.path == "/trickle":
                for value in body:
                    self.wfile.write(bytes([value]))
                    self.wfile.flush()
                    time.sleep(0.03)
            else:
                self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass


class TransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
        cls.server.paths = []
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.origin = "http://127.0.0.1:%s" % cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def fetch(self, path, **kwargs):
        self.assertTrue(callable(getattr(check, "fetch_page", None)), "missing transport")
        return check.fetch_page(self.origin + path, require_https=False, **kwargs)

    def test_loopback_fetch_and_same_host_redirect(self):
        self.assertIn("Release amber-2026", self.fetch("/same-host"))

    def test_cross_host_redirect_is_rejected_before_destination_request(self):
        self.server.paths.clear()
        with self.assertRaisesRegex(ValueError, "redirect"):
            self.fetch("/external")
        self.assertEqual(self.server.paths, ["/external"])

    def test_response_body_size_is_bounded(self):
        with self.assertRaisesRegex(ValueError, "body|large|limit"):
            self.fetch("/large", max_bytes=100)

    def test_trickle_response_cannot_extend_read_deadline_indefinitely(self):
        with self.assertRaisesRegex(ValueError, "time limit"):
            self.fetch("/trickle", timeout=0.08)

    def test_actual_network_failure_is_actionable(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        self.assertTrue(callable(getattr(check, "fetch_page", None)), "missing transport")
        with self.assertRaisesRegex(ValueError, "reachable|fetch|connect"):
            check.fetch_page("http://127.0.0.1:%s/" % port, require_https=False, timeout=0.2)

    def test_protected_comparison_page_cannot_be_bypassed_by_expected_text(self):
        self.assertTrue(callable(getattr(check, "verify", None)), "missing verifier")
        def transport(url):
            return self.fetch("/protected" if url == DEPLOYMENT else "/current")
        result = check.verify(CUSTOM, deployment_url=DEPLOYMENT,
                              expect_text=["Release amber-2026"], fetcher=transport)
        self.assertEqual(result["status"], "pending")
        self.assertIn("401", " ".join(result["errors"]))

    def test_www_alias_and_non_https_are_rejected_by_verifier(self):
        self.assertTrue(callable(getattr(check, "validate_url", None)), "missing URL validation")
        self.assertTrue(callable(getattr(check, "verify", None)), "missing verifier")
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            check.validate_url(self.origin)
        self.assertTrue(callable(getattr(check, "SameHostRedirect", None)), "missing redirect guard")
        guard = check.SameHostRedirect(CUSTOM)
        with self.assertRaisesRegex(ValueError, "redirect"):
            guard.redirect_request(None, None, 302, "Found", {}, "https://www.agentverse.example.org")

    def test_verification_orchestration_passes_current_fixture_and_fails_network(self):
        self.assertTrue(callable(getattr(check, "verify", None)), "missing verifier")
        result = check.verify(CUSTOM, deployment_url=DEPLOYMENT,
                              fetcher=lambda _: self.fetch("/current"))
        self.assertEqual(result["status"], "verified")
        def offline(_):
            raise ValueError("Cannot fetch URL: connection refused")
        self.assertEqual(check.verify(CUSTOM, fetcher=offline)["status"], "pending")


if __name__ == "__main__":
    unittest.main()
