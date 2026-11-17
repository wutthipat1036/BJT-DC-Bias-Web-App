# Input Units Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let users enter resistor values in Ω/kΩ/MΩ and voltages in V/mV, while all engineering maths stays in SI units.

**Architecture:** `app.py` owns the unit metadata (code, factor, display label) and converts every submitted value to SI before calling `dc_bias.py`. The template renders one small `<select>` per input from that metadata. `dc_bias.py` is unchanged because it already works in Ω and V.

**Tech Stack:** Flask 3.1, Jinja2, vanilla JS, unittest.

**Spec:** This plan (short design for a small change).

## Global Constraints

- Default units must remain kΩ for resistors and V for voltages, so existing results do not change.
- Resistor units: `ohm` (Ω), `k` (kΩ), `meg` (MΩ). Voltage units: `v` (V), `mv` (mV).
- Invalid or unknown unit codes must produce HTTP 400 with the existing Thai validation alert.
- Engineering logic must stay in `dc_bias.py`; `app.py` only converts units.
- UI text and validation messages stay in Thai, matching the existing app.

## Review Focus

- A value submitted with `meg` must equal the same value in `k` (e.g. `0.47 meg` = `470 k`).
- A voltage submitted in `mv` must equal the same value in `v` (e.g. `700 mv` = `0.70 v`).
- A tampered/unknown unit code must not silently fall back; it must return 400.
- The circuit schematic must show the unit the user actually typed, not a hard-coded kΩ.
- Existing POST payloads without unit fields must keep working (default units).

---

### Task 1: Unit conversion helpers in `app.py`

**Files:**
- Modify: `app.py`
- Test: `tests/test_web.py`

**Interfaces:**
- Produces:
  - `RESISTOR_UNITS = {"ohm": {"factor": 1.0, "label": "Ω"}, "k": {"factor": 1000.0, "label": "kΩ"}, "meg": {"factor": 1_000_000.0, "label": "MΩ"}}`
  - `VOLTAGE_UNITS = {"v": {"factor": 1.0, "label": "V"}, "mv": {"factor": 0.001, "label": "mV"}}`
  - `_parse_quantity(field: str, raw_value: str, raw_unit: str, units: dict, default_unit: str) -> float`

- [ ] **Step 1: Write the failing tests** in `tests/test_web.py`

```python
def test_post_megohm_unit_matches_kilohm(self):
    data = dict(FIXED, rb="0.47", rb_unit="meg", rc_unit="k", vcc_unit="v", vbe_unit="v")
    response = self.client.post("/", data=data)
    self.assertEqual(response.status_code, 200)
    self.assertIn("6.71", response.get_data(as_text=True))

def test_post_millivolt_unit_matches_volt(self):
    data = dict(VALID, vbe="700", vbe_unit="mv", vcc_unit="v")
    response = self.client.post("/", data=data)
    self.assertEqual(response.status_code, 200)
    self.assertIn("8.78", response.get_data(as_text=True))

def test_post_invalid_unit_shows_error(self):
    data = dict(VALID, rc_unit="garbage")
    response = self.client.post("/", data=data)
    self.assertEqual(response.status_code, 400)
    self.assertIn("ข้อมูลไม่ถูกต้อง", response.get_data(as_text=True))
```

- [ ] **Step 2: Run tests and confirm they fail**

Run: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`
Expected: the three new tests fail (the meg/mv cases currently ignore the unit, the invalid-unit case currently returns 200).

- [ ] **Step 3: Implement the metadata and helper** in `app.py`

Add the two dictionaries after `BIAS_TYPES`, add `_parse_quantity` after `_parse_float`, and replace every `_parse_float(...) * KILO` with `_parse_quantity(...)` using the matching unit dictionary and default.

- [ ] **Step 4: Run tests and confirm they pass**

Run: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`
Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_web.py
git commit -m "Support resistor and voltage unit conversion"
```

### Task 2: Per-field unit dropdowns in the template

**Files:**
- Modify: `templates/index.html`
- Modify: `app.py` (pass `RESISTOR_UNITS` and `VOLTAGE_UNITS` to the template)

**Interfaces:**
- Consumes: `RESISTOR_UNITS`, `VOLTAGE_UNITS` from Task 1.
- Produces: form fields `vcc_unit`, `vbe_unit`, `rb_unit`, `r1_unit`, `r2_unit`, `rc_unit`, `re_unit`.

- [ ] **Step 1: Pass unit metadata to the template**

In `index()`, add `resistor_units=RESISTOR_UNITS, voltage_units=VOLTAGE_UNITS` to `render_template`.

- [ ] **Step 2: Add the dropdowns**

Replace each static `<span class="unit">…</span>` with a `<select class="unit-select" name="<field>_unit">` rendered from the matching dictionary. Add `has-unit` to the `.input-wrap`. Defaults come from `form.<field>_unit`.

- [ ] **Step 3: Update schematic labels**

Change every `{{ form.rc }} kΩ` style label to `{{ form.rc }} {{ resistor_units[form.rc_unit].label }}` (and the same for the other resistor labels).

- [ ] **Step 4: Verify the rendered page**

Run a GET and confirm the HTML contains `name="rc_unit"`, `name="vcc_unit"`, and the Ω/MΩ options.

### Task 3: Style the unit dropdowns

**Files:**
- Modify: `static/style.css`

- [ ] **Step 1: Add styles**

Add `.input-wrap.has-unit input { padding-right: 5rem; }` and a compact `.unit-select` rule positioned at the right edge of the input.

- [ ] **Step 2: Verify visually**

Open the page in the browser and confirm the dropdown does not overlap the typed value at desktop and mobile widths.

### Task 4: Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/validation.md`
- Modify: `docs/design-note.md`

- [ ] **Step 1: Document the supported units and the conversion rule**

Add one line per file: resistors Ω/kΩ/MΩ, voltages V/mV, converted to SI before calculation.

### Task 5: Final verification and commit

- [ ] **Step 1: Run the full suite**

Run: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`
Expected: all tests pass.

- [ ] **Step 2: Verify over HTTP**

POST `rb=0.47&rb_unit=meg` and confirm it matches `rb=470&rb_unit=k`; POST `vbe=700&vbe_unit=mv` and confirm it matches `vbe=0.70&vbe_unit=v`.

- [ ] **Step 3: Commit and push**

```bash
git add -A
git commit -m "Add per-field unit selection for inputs"
git push origin main
```
