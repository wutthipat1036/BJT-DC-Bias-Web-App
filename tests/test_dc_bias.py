"""Unit tests for the pure engineering logic in :mod:`dc_bias`.

Run with::

    python -m unittest discover -s tests -v
"""

import sys
import unittest
from pathlib import Path

# Make the project root importable regardless of how discovery is invoked.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dc_bias import (  # noqa: E402
    ACTIVE,
    CUTOFF,
    SATURATION,
    ValidationError,
    compute_voltage_divider_bias,
)

# Reference component values from the lab handout (resistors in Ω).
REF = {
    "vcc": 12.0,
    "r1": 100_000.0,
    "r2": 22_000.0,
    "rc": 2_200.0,
    "re": 1_000.0,
    "beta": 100.0,
    "vbe": 0.70,
}


class ReferenceCalculationTest(unittest.TestCase):
    def test_reference_operating_point(self):
        result = compute_voltage_divider_bias(**REF)
        # Approximate analysis (I_B ≈ 0)
        self.assertAlmostEqual(result.vb, 2.164, delta=0.01)
        self.assertAlmostEqual(result.ve, 1.464, delta=0.01)
        self.assertAlmostEqual(result.vc, 8.779, delta=0.01)
        self.assertAlmostEqual(result.vce, 7.315, delta=0.01)
        self.assertAlmostEqual(result.ic_ma, 1.464, delta=0.01)

    def test_reference_is_active(self):
        result = compute_voltage_divider_bias(**REF)
        self.assertEqual(result.region, ACTIVE)
        self.assertTrue(result.is_active)
        self.assertEqual(result.warnings, [])


class ValidationTest(unittest.TestCase):
    def test_zero_resistor_rejected(self):
        with self.assertRaises(ValidationError):
            compute_voltage_divider_bias(**dict(REF, r1=0.0))

    def test_negative_beta_rejected(self):
        with self.assertRaises(ValidationError):
            compute_voltage_divider_bias(**dict(REF, beta=-5.0))

    def test_zero_vcc_rejected(self):
        with self.assertRaises(ValidationError):
            compute_voltage_divider_bias(**dict(REF, vcc=0.0))

    def test_non_numeric_rejected(self):
        with self.assertRaises(ValidationError):
            compute_voltage_divider_bias(**dict(REF, vbe="x"))


class RegionWarningTest(unittest.TestCase):
    def test_cutoff_when_vth_below_vbe(self):
        # V_TH ≈ 0.119 V < V_BE (0.7 V) → cut-off.
        result = compute_voltage_divider_bias(**dict(REF, r2=1_000.0))
        self.assertEqual(result.region, CUTOFF)
        self.assertTrue(result.warnings)

    def test_saturation_when_vce_too_low(self):
        # A large R_C drives V_CE negative → saturation.
        result = compute_voltage_divider_bias(**dict(REF, rc=10_000.0))
        self.assertEqual(result.region, SATURATION)
        self.assertTrue(result.warnings)


if __name__ == "__main__":
    unittest.main()
