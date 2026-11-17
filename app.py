"""Flask web application for the BJT common-emitter DC bias calculator.

The web layer only handles HTTP, unit conversion (kΩ → Ω for the UI) and
rendering. All engineering maths lives in :mod:`dc_bias`.
"""

from __future__ import annotations

from flask import Flask, render_template, request

from dc_bias import (
    BiasResult,
    ValidationError,
    compute_emitter_bias,
    compute_fixed_bias,
    compute_voltage_divider_bias,
)

app = Flask(__name__)

#: Supported bias topologies (values match the ``<option>`` values in the UI).
BIAS_TYPES = ("voltage_divider", "fixed", "emitter")

#: Unit metadata for the UI: code -> conversion factor to SI + display label.
#: The engineering module works in Ω and V, so we convert on the boundary.
RESISTOR_UNITS = {
    "ohm": {"factor": 1.0, "label": "Ω"},
    "k": {"factor": 1_000.0, "label": "kΩ"},
    "meg": {"factor": 1_000_000.0, "label": "MΩ"},
}
VOLTAGE_UNITS = {
    "v": {"factor": 1.0, "label": "V"},
    "mv": {"factor": 0.001, "label": "mV"},
}

DEFAULT_FORM = {
    "bias_type": "voltage_divider",
    "vcc": "12",
    "vcc_unit": "v",
    "r1": "100",
    "r1_unit": "k",
    "r2": "22",
    "r2_unit": "k",
    "rb": "470",
    "rb_unit": "k",
    "rc": "2.2",
    "rc_unit": "k",
    "re": "1",
    "re_unit": "k",
    "beta": "100",
    "vbe": "0.70",
    "vbe_unit": "v",
}

#: Presentation-only formula captions shown under each schematic. The actual
#: engineering maths lives in :mod:`dc_bias`; these are static labels only.
BIAS_FORMULAS = {
    "voltage_divider": {
        "title": "สมการ (Approximate, I<sub>B</sub> ≈ 0)",
        "body": (
            "V<sub>B</sub> = V<sub>CC</sub>·R<sub>2</sub>/(R<sub>1</sub>+R<sub>2</sub>)"
            " · V<sub>E</sub> = V<sub>B</sub>−V<sub>BE</sub>"
            " · I<sub>C</sub> ≈ I<sub>E</sub> = V<sub>E</sub>/R<sub>E</sub>"
        ),
    },
    "fixed": {
        "title": "สมการ",
        "body": (
            "I<sub>B</sub> = (V<sub>CC</sub>−V<sub>BE</sub>)/R<sub>B</sub>"
            " · I<sub>C</sub> = β·I<sub>B</sub>"
            " · V<sub>CE</sub> = V<sub>CC</sub>−I<sub>C</sub>·R<sub>C</sub>"
        ),
    },
    "emitter": {
        "title": "สมการ",
        "body": (
            "I<sub>B</sub> = (V<sub>CC</sub>−V<sub>BE</sub>)"
            "/(R<sub>B</sub>+(β+1)R<sub>E</sub>)"
            " · V<sub>E</sub> = I<sub>E</sub>·R<sub>E</sub>"
            " · V<sub>CE</sub> = V<sub>CC</sub>−I<sub>C</sub>R<sub>C</sub>"
            "−I<sub>E</sub>R<sub>E</sub>"
        ),
    },
}


def _parse_float(field: str, raw: str) -> float:
    """Convert a form field to float, raising a friendly ValidationError."""
    text = (raw or "").strip()
    if text == "":
        raise ValidationError(f"กรุณากรอกค่า {field.upper()} ให้ครบ")
    try:
        return float(text)
    except ValueError:
        raise ValidationError(f"ค่า {field.upper()} = '{raw}' ไม่ใช่ตัวเลข") from None


def _parse_quantity(
    field: str,
    raw_value: str,
    raw_unit: str,
    units: dict[str, dict],
    default_unit: str,
) -> float:
    """Convert a numeric form field plus its unit code into SI units."""
    value = _parse_float(field, raw_value)
    unit = (raw_unit or default_unit).strip()
    if unit not in units:
        raise ValidationError(f"หน่วยของ {field.upper()} ไม่ถูกต้อง")
    return value * units[unit]["factor"]


def _build_result(form: dict[str, str]) -> BiasResult:
    """Convert the raw form values (any supported unit) into SI units."""
    bias_type = form.get("bias_type", "voltage_divider")
    if bias_type not in BIAS_TYPES:
        raise ValidationError(f"ไม่รู้จักชนิดไบแอส '{bias_type}'")

    vcc = _parse_quantity(
        "vcc", form["vcc"], form.get("vcc_unit"), VOLTAGE_UNITS, "v"
    )
    beta = _parse_float("beta", form["beta"])
    vbe = _parse_quantity(
        "vbe", form["vbe"], form.get("vbe_unit"), VOLTAGE_UNITS, "v"
    )
    rc = _parse_quantity(
        "rc", form["rc"], form.get("rc_unit"), RESISTOR_UNITS, "k"
    )

    if bias_type == "fixed":
        rb = _parse_quantity(
            "rb", form["rb"], form.get("rb_unit"), RESISTOR_UNITS, "k"
        )
        return compute_fixed_bias(vcc=vcc, rb=rb, rc=rc, beta=beta, vbe=vbe)

    if bias_type == "emitter":
        rb = _parse_quantity(
            "rb", form["rb"], form.get("rb_unit"), RESISTOR_UNITS, "k"
        )
        re = _parse_quantity(
            "re", form["re"], form.get("re_unit"), RESISTOR_UNITS, "k"
        )
        return compute_emitter_bias(
            vcc=vcc, rb=rb, rc=rc, re=re, beta=beta, vbe=vbe
        )

    r1 = _parse_quantity(
        "r1", form["r1"], form.get("r1_unit"), RESISTOR_UNITS, "k"
    )
    r2 = _parse_quantity(
        "r2", form["r2"], form.get("r2_unit"), RESISTOR_UNITS, "k"
    )
    re = _parse_quantity(
        "re", form["re"], form.get("re_unit"), RESISTOR_UNITS, "k"
    )
    return compute_voltage_divider_bias(
        vcc=vcc, r1=r1, r2=r2, rc=rc, re=re, beta=beta, vbe=vbe
    )


@app.route("/", methods=["GET", "POST"])
def index():
    """Render the calculator. GET shows defaults; POST computes a result."""
    form = dict(DEFAULT_FORM)
    result: BiasResult | None = None
    error: str | None = None
    status = 200

    if request.method == "POST":
        # Fields hidden by the selected bias type are not submitted at all;
        # fall back to their defaults, but keep explicitly cleared fields empty
        # so validation still reports them.
        form = {
            field: (
                request.form.get(field, "").strip()
                if field in request.form
                else DEFAULT_FORM[field]
            )
            for field in DEFAULT_FORM
        }
        try:
            result = _build_result(form)
        except ValidationError as exc:
            error = str(exc)
            status = 400

    return (
        render_template(
            "index.html",
            form=form,
            result=result,
            error=error,
            formulas=BIAS_FORMULAS,
            resistor_units=RESISTOR_UNITS,
            voltage_units=VOLTAGE_UNITS,
        ),
        status,
    )


if __name__ == "__main__":
    # Development server only — never expose this to a public network.
    app.run(debug=True)
