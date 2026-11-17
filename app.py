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

#: UI inputs are expressed in kΩ for the resistors; the engineering module
#: works in Ω, so we convert on the boundary.
KILO = 1000.0

#: Supported bias topologies (values match the ``<option>`` values in the UI).
BIAS_TYPES = ("voltage_divider", "fixed", "emitter")

DEFAULT_FORM = {
    "bias_type": "voltage_divider",
    "vcc": "12",
    "r1": "100",
    "r2": "22",
    "rb": "470",
    "rc": "2.2",
    "re": "1",
    "beta": "100",
    "vbe": "0.70",
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


def _build_result(form: dict[str, str]) -> BiasResult:
    """Convert the raw form values (kΩ) into SI units and compute the bias."""
    bias_type = form.get("bias_type", "voltage_divider")
    if bias_type not in BIAS_TYPES:
        raise ValidationError(f"ไม่รู้จักชนิดไบแอส '{bias_type}'")

    vcc = _parse_float("vcc", form["vcc"])
    beta = _parse_float("beta", form["beta"])
    vbe = _parse_float("vbe", form["vbe"])
    rc = _parse_float("rc", form["rc"]) * KILO

    if bias_type == "fixed":
        rb = _parse_float("rb", form["rb"]) * KILO
        return compute_fixed_bias(vcc=vcc, rb=rb, rc=rc, beta=beta, vbe=vbe)

    if bias_type == "emitter":
        rb = _parse_float("rb", form["rb"]) * KILO
        re = _parse_float("re", form["re"]) * KILO
        return compute_emitter_bias(
            vcc=vcc, rb=rb, rc=rc, re=re, beta=beta, vbe=vbe
        )

    r1 = _parse_float("r1", form["r1"]) * KILO
    r2 = _parse_float("r2", form["r2"]) * KILO
    re = _parse_float("re", form["re"]) * KILO
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
        ),
        status,
    )


if __name__ == "__main__":
    # Development server only — never expose this to a public network.
    app.run(debug=True)
