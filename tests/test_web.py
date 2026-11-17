"""HTTP-level tests for the Flask application.

Run with::

    python -m unittest discover -s tests -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app  # noqa: E402

VALID = {
    "bias_type": "voltage_divider",
    "vcc": "12",
    "r1": "100",
    "r2": "22",
    "rc": "2.2",
    "re": "1",
    "beta": "100",
    "vbe": "0.70",
}

FIXED = {
    "bias_type": "fixed",
    "vcc": "12",
    "rb": "470",
    "rc": "2.2",
    "beta": "100",
    "vbe": "0.70",
}

EMITTER = {
    "bias_type": "emitter",
    "vcc": "12",
    "rb": "470",
    "rc": "2.2",
    "re": "1",
    "beta": "100",
    "vbe": "0.70",
}


class WebRouteTest(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_get_home_ok(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("Calculate DC Bias", body)
        self.assertIn("Fixed Bias", body)
        self.assertIn("Emitter Bias", body)

    def test_post_valid_computes_results(self):
        response = self.client.post("/", data=VALID)
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("Active region approximation OK", body)
        # V_C reference value (approximate analysis, 2 dp display).
        self.assertIn("8.78", body)

    def test_post_fixed_bias(self):
        response = self.client.post("/", data=FIXED)
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("Active region approximation OK", body)
        # V_C = 12 − 2.4043 mA × 2.2 kΩ = 6.71 V
        self.assertIn("6.71", body)

    def test_post_emitter_bias(self):
        response = self.client.post("/", data=EMITTER)
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("Active region approximation OK", body)
        # V_C = 12 − 1.979 mA × 2.2 kΩ = 7.65 V
        self.assertIn("7.65", body)

    def test_post_unknown_bias_type_shows_error(self):
        response = self.client.post("/", data=dict(VALID, bias_type="nope"))
        self.assertEqual(response.status_code, 400)
        self.assertIn("ข้อมูลไม่ถูกต้อง", response.get_data(as_text=True))

    def test_post_megohm_unit_matches_kilohm(self):
        data = dict(
            FIXED,
            rb="0.47",
            rb_unit="meg",
            rc_unit="k",
            vcc_unit="v",
            vbe_unit="v",
        )
        response = self.client.post("/", data=data)
        self.assertEqual(response.status_code, 200)
        # 0.47 MΩ must behave exactly like 470 kΩ → V_C = 6.71 V.
        self.assertIn("6.71", response.get_data(as_text=True))

    def test_post_millivolt_unit_matches_volt(self):
        data = dict(VALID, vbe="700", vbe_unit="mv", vcc_unit="v")
        response = self.client.post("/", data=data)
        self.assertEqual(response.status_code, 200)
        # 700 mV must behave exactly like 0.70 V → V_C = 8.78 V.
        self.assertIn("8.78", response.get_data(as_text=True))

    def test_post_invalid_unit_shows_error(self):
        response = self.client.post("/", data=dict(VALID, rc_unit="garbage"))
        self.assertEqual(response.status_code, 400)
        self.assertIn("ข้อมูลไม่ถูกต้อง", response.get_data(as_text=True))

    def test_post_invalid_shows_error(self):
        response = self.client.post("/", data=dict(VALID, r1="0"))
        self.assertEqual(response.status_code, 400)
        self.assertIn("ข้อมูลไม่ถูกต้อง", response.get_data(as_text=True))

    def test_post_non_numeric_shows_error(self):
        response = self.client.post("/", data=dict(VALID, vcc="abc"))
        self.assertEqual(response.status_code, 400)
        self.assertIn("ไม่ใช่ตัวเลข", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
