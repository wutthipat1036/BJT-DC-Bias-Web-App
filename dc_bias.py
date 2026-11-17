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
The *approximate* voltage-divider analysis is used: the base current is
assumed negligible (I_B ≈ 0), so the R1/R2 divider sets the base voltage
directly. The Forward-Active approximation uses a constant β and a constant
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
    bias_type: str = "voltage_divider"
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

    Uses the **approximate** analysis (I_B ≈ 0): the divider voltage V_TH is
    taken directly as V_B, so the base current does not load the divider.

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

    # Approximate voltage-divider analysis: I_B ≈ 0, so the divider sets V_B.
    vth = vcc * r2 / (r1 + r2)
    rth = r1 * r2 / (r1 + r2)  # informational only (not used by the approximation)

    vb = vth
    ve = vb - vbe
    ie = ve / re
    ic = ie  # I_B ≈ 0 → I_C ≈ I_E
    ib = ic / beta

    # Node voltages
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
        bias_type="voltage_divider",
        warnings=warnings,
    )


def _classify_single_resistor_bias(
    ib: float, vce: float, cutoff_reason: str
) -> tuple[str, List[str]]:
    """Classify the operating region for a single-base-resistor bias circuit.

    ``ib`` is the solved base current: a non-positive value means the device is
    cut off. ``cutoff_reason`` is the type-specific warning message.
    """
    warnings: List[str] = []
    if ib <= 0:
        return CUTOFF, [cutoff_reason]
    if vce <= SATURATION_VCE:
        return SATURATION, [
            "V_CE ≤ 0.2 V: ทรานซิสเตอร์อิ่มตัว (Saturation) "
            "— แบบจำลอง Forward-Active ใช้ไม่ได้"
        ]
    if vce < 0:
        return SATURATION, [
            "V_CE ติดลบ: ไบแอสมากเกินไปจนทรานซิสเตอร์อิ่มตัวลึก"
        ]
    return ACTIVE, warnings


def compute_fixed_bias(
    vcc: float,
    rb: float,
    rc: float,
    beta: float,
    vbe: float,
) -> BiasResult:
    """Compute the DC operating point of an NPN **fixed bias** circuit.

    A single base resistor ``R_B`` connects V_CC to the base and the emitter is
    grounded (``R_E = 0``). The base current is set by ``R_B`` alone::

        I_B = (V_CC − V_BE) / R_B
        I_C = β · I_B
        V_CE = V_CC − I_C · R_C   (V_E = 0)

    Parameters are in SI units (Ω, V). Returns a :class:`BiasResult` whose
    currents are in amperes. Raises :class:`ValidationError` for invalid input.
    """
    _require_positive("VCC", vcc)
    _require_positive("RB", rb)
    _require_positive("RC", rc)
    _require_positive("β", beta)
    _require_positive("VBE", vbe)

    ib = (vcc - vbe) / rb
    ic = beta * ib
    ie = (beta + 1.0) * ib

    # Node voltages (the emitter is tied directly to ground).
    vb = vbe
    ve = 0.0
    vc = vcc - ic * rc
    vce = vc - ve

    region, warnings = _classify_single_resistor_bias(
        ib,
        vce,
        "V_CC ≤ V_BE: ทรานซิสเตอร์อยู่ในช่วง Cut-off "
        "(แบบจำลอง Forward-Active ใช้ไม่ได้)",
    )

    return BiasResult(
        vcc=vcc,
        r1=rb,  # fixed bias uses a single base resistor instead of a divider
        r2=0.0,
        rc=rc,
        re=0.0,
        beta=beta,
        vbe=vbe,
        vth=0.0,
        rth=0.0,
        ib=ib,
        ic=ic,
        ie=ie,
        vb=vb,
        ve=ve,
        vc=vc,
        vce=vce,
        region=region,
        bias_type="fixed",
        warnings=warnings,
    )


def compute_emitter_bias(
    vcc: float,
    rb: float,
    rc: float,
    re: float,
    beta: float,
    vbe: float,
) -> BiasResult:
    """Compute the DC operating point of an NPN **emitter-stabilized** bias circuit.

    A base resistor ``R_B`` connects V_CC to the base and an emitter resistor
    ``R_E`` provides negative feedback. Writing the base loop with
    ``I_E = (β + 1)·I_B`` gives::

        I_B = (V_CC − V_BE) / (R_B + (β + 1)·R_E)
        I_C = β · I_B
        I_E = (β + 1)·I_B
        V_E = I_E · R_E
        V_B = V_E + V_BE
        V_CE = V_CC − I_C·R_C − I_E·R_E

    Parameters are in SI units (Ω, V). Returns a :class:`BiasResult` whose
    currents are in amperes. Raises :class:`ValidationError` for invalid input.
    """
    _require_positive("VCC", vcc)
    _require_positive("RB", rb)
    _require_positive("RC", rc)
    _require_positive("RE", re)
    _require_positive("β", beta)
    _require_positive("VBE", vbe)

    ib = (vcc - vbe) / (rb + (beta + 1.0) * re)
    ic = beta * ib
    ie = (beta + 1.0) * ib

    # Node voltages
    ve = ie * re
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve

    region, warnings = _classify_single_resistor_bias(
        ib,
        vce,
        "V_CC ≤ V_BE: ทรานซิสเตอร์อยู่ในช่วง Cut-off "
        "(แบบจำลอง Forward-Active ใช้ไม่ได้)",
    )

    return BiasResult(
        vcc=vcc,
        r1=rb,  # emitter bias uses a single base resistor instead of a divider
        r2=0.0,
        rc=rc,
        re=re,
        beta=beta,
        vbe=vbe,
        vth=0.0,
        rth=0.0,
        ib=ib,
        ic=ic,
        ie=ie,
        vb=vb,
        ve=ve,
        vc=vc,
        vce=vce,
        region=region,
        bias_type="emitter",
        warnings=warnings,
    )
