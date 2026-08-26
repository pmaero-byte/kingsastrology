from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app.main import create_app


class CaravanseraiApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())
        self.ts = 1787741820000  # 2026-08-26 10:57 UT

    def test_zij_manifest(self) -> None:
        r = self.client.get("/api/v1/zij/manifest")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertIn("constants_sha256", body)
        self.assertIn("pinned_sample", body)

    def test_sky_payload_full_provenance(self) -> None:
        r = self.client.get(f"/api/v1/sky?timestamp_ms_utc={self.ts}&lat=28.61&lon=77.21")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertIn("tier", body["zij"])
        self.assertIn("factors", body["qanun"])
        self.assertIn("hijri", body["calendars"])
        self.assertFalse(body["qanun"]["provenance"]["runtime_ai"])

    def test_calendars_endpoint(self) -> None:
        r = self.client.get(f"/api/v1/calendars?timestamp_ms_utc={self.ts}")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        for era in ("hijri", "jalali", "vikram_samvat", "saka", "kali"):
            self.assertIn(era, body)

    def test_crescent_endpoint(self) -> None:
        r = self.client.get(
            f"/api/v1/crescent?timestamp_ms_utc={self.ts}&lat=28.61&lon=77.21&elev_m=216"
        )
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertIn("yallop_q", body)
        self.assertEqual(body["yallop_q"]["tier"], "hypothesis")

    def test_crescent_requires_location(self) -> None:
        r = self.client.get(f"/api/v1/crescent?timestamp_ms_utc={self.ts}")
        self.assertEqual(r.status_code, 422)

    def test_tribunal_endpoint(self) -> None:
        r = self.client.get("/api/v1/tribunal")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        types = {e["type"] for e in body["entries"]}
        self.assertIn("verification", types)
        self.assertIn("limitation", types)
        self.assertIn("retraction", types)
        self.assertIn("pre_registration", types)

    def test_tribunal_page_served(self) -> None:
        r = self.client.get("/tribunal")
        self.assertEqual(r.status_code, 200)
        self.assertIn("The Tribunal", r.text)

    def test_openapi_documents_caravanserai(self) -> None:
        r = self.client.get("/openapi.json")
        self.assertEqual(r.status_code, 200)
        paths = r.json()["paths"]
        for path in ("/api/v1/sky", "/api/v1/crescent", "/api/v1/tribunal"):
            self.assertIn(path, paths)


if __name__ == "__main__":
    unittest.main()
