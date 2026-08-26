from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app.main import create_app


class SpacetimeClockRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def test_clock_page_is_served(self) -> None:
        response = self.client.get("/clock")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Spacetime Clock", response.text)
        self.assertIn("ephemeris.js", response.text)

    def test_clock_assets_are_served(self) -> None:
        for asset in ("clock.js", "ephemeris.js", "clock.css"):
            response = self.client.get(f"/assets/{asset}")
            self.assertEqual(response.status_code, 200, asset)


if __name__ == "__main__":
    unittest.main()
