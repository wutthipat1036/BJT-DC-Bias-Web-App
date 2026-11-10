"""DC bias calculations for an NPN BJT common-emitter voltage-divider bias circuit.

This module is *pure engineering logic*: it knows nothing about HTML, HTTP or
Flask. That separation lets the same functions be unit-tested independently of
the web layer.

Units
-----
* Resistances are in ohms (Ω).
* Voltages are in volts (V).
* Currents are returned in amperes (A). Convenience ``*_ma`` properties are
  provided for display in milliamperes (mA).

Model
-----
The Forward-Active approximation is used with a constant β and a constant
V_BE. Results outside the forward-active region are still computed but are
flagged with warnings; callers must not present them as trustworthy without
surfacing those warnings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

#: Below this V_CE (V) the transistor is treated as saturated.
SATURATION_VCE = 0.2

#: Recognised operating-region identifiers.
ACTIVE = "active"
SATURATION = "saturation"
CUTOFF = "cutoff"


class ValidationError(ValueError):
    """Raised when an input parameter is missing or physically invalid."""


@dataclass
class BiasResult:
    """The DC operating point plus the intermediate values used to find it."""

    # Inputs (echoed back for transparency)
    vcc: float
    r1: float
    r2: float
    rc: float
    re: float
    beta: float
    vbe: float

    # Intermediate values
    vth: float  # Thevenin base voltage (V)
    rth: float  # Thevenin base resistance (Ω)

    # Currents (A)
    ib: float
    ic: float
    ie: float

    # Voltages (V)
    vb: float
    ve: float
    vc: float
    vce: float

    # Operating region + human-readable warnings
    region: str
    warnings: List[str] = field(default_factory=list)

    @property
    def ib_ma(self) -> float:
        return self.ib * 1000.0

    @property
    def ic_ma(self) -> float:
        return self.ic * 1000.0

    @property
    def ie_ma(self) -> float:
        return self.ie * 1000.0

    @property
    def is_active(self) -> bool:
        return self.region == ACTIVE


def _require_positive(name: str, value: float) -> None:
    """Validate that *value* is a real, finite number greater than zero."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{name} ต้องเป็นตัวเลข")
    if value != value or value in (float("inf"), float("-inf")):  # NaN / inf
        raise ValidationError(f"{name} ต้องเป็นจำนวนจริงที่จำกัด")
    if value <= 0:
        raise ValidationError(f"{name} ต้องมากกว่า 0")


def compute_voltage_divider_bias(
    vcc: float,
    r1: float,
    r2: float,
    rc: float,
    re: float,
    beta: float,
    vbe: float,
) -> BiasResult:
    """Compute the DC operating point of an NPN voltage-divider bias circuit.

    Parameters are in SI units (Ω, V). Returns a :class:`BiasResult` whose
    currents are in amperes. Raises :class:`ValidationError` for invalid input.
    """
    _require_positive("VCC", vcc)
    _require_positive("R1", r1)
    _require_positive("R2", r2)
    _require_positive("RC", rc)
    _require_positive("RE", re)
    _require_positive("β", beta)
    _require_positive("VBE", vbe)

    # Thevenin equivalent of the base divider
    vth = vcc * r2 / (r1 + r2)
    rth = r1 * r2 / (r1 + r2)

    # Base current from the Thevenin loop
    ib = (vth - vbe) / (rth + (beta + 1.0) * re)
    ic = beta * ib
    ie = (beta + 1.0) * ib

    # Node voltages
    ve = ie * re
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve

    # Operating region
    warnings: List[str] = []
    if vth <= vbe:
        region = CUTOFF
        warnings.append(
            "V_TH ≤ V_BE: ทรานซิสเตอร์อยู่ในช่วง Cut-off "
            "(แบบจำลอง Forward-Active ใช้ไม่ได้)"
        )
    elif vce <= SATURATION_VCE:
        region = SATURATION
        warnings.append(
            "V_CE ≤ 0.2 V: ทรานซิสเตอร์อิ่มตัว (Saturation) "
            "— แบบจำลอง Forward-Active ใช้ไม่ได้"
        )
    else:
        region = ACTIVE

    if vce < 0 and region != CUTOFF:
        region = SATURATION
        warnings.append(
            "V_CE ติดลบ: ไบแอสมากเกินไปจนทรานซิสเตอร์อิ่มตัวลึก"
        )

    return BiasResult(
        vcc=vcc,
        r1=r1,
        r2=r2,
        rc=rc,
        re=re,
        beta=beta,
        vbe=vbe,
        vth=vth,
        rth=rth,
        ib=ib,
        ic=ic,
        ie=ie,
        vb=vb,
        ve=ve,
        vc=vc,
        vce=vce,
        region=region,
        warnings=warnings,
    )
