"""Flask web application for the BJT common-emitter DC bias calculator.

The web layer only handles HTTP, unit conversion (kΩ → Ω for the UI) and
rendering. All engineering maths lives in :mod:`dc_bias`.
"""

from __future__ import annotations

from flask import Flask, render_template, request

from dc_bias import BiasResult, ValidationError, compute_voltage_divider_bias

app = Flask(__name__)

#: UI inputs are expressed in kΩ for the resistors; the engineering module
#: works in Ω, so we convert on the boundary.
KILO = 1000.0

DEFAULT_FORM = {
    "vcc": "12",
    "r1": "100",
    "r2": "22",
    "rc": "2.2",
    "re": "1",
    "beta": "100",
    "vbe": "0.70",
}

#: Fields that are resistor values entered in kΩ.
RESISTOR_FIELDS = ("r1", "r2", "rc", "re")


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
    vcc = _parse_float("vcc", form["vcc"])
    beta = _parse_float("beta", form["beta"])
    vbe = _parse_float("vbe", form["vbe"])

    resistors = {
        field: _parse_float(field, form[field]) * KILO
        for field in RESISTOR_FIELDS
    }

    return compute_voltage_divider_bias(
        vcc=vcc,
        r1=resistors["r1"],
        r2=resistors["r2"],
        rc=resistors["rc"],
        re=resistors["re"],
        beta=beta,
        vbe=vbe,
    )


@app.route("/", methods=["GET", "POST"])
def index():
    """Render the calculator. GET shows defaults; POST computes a result."""
    form = dict(DEFAULT_FORM)
    result: BiasResult | None = None
    error: str | None = None
    status = 200

    if request.method == "POST":
        form = {field: request.form.get(field, "").strip() for field in DEFAULT_FORM}
        try:
            result = _build_result(form)
        except ValidationError as exc:
            error = str(exc)
            status = 400

    return (
        render_template("index.html", form=form, result=result, error=error),
        status,
    )


if __name__ == "__main__":
    # Development server only — never expose this to a public network.
    app.run(debug=True)
