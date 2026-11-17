# BJT DC Bias Web App

Flask Web Application สำหรับคำนวณ **DC Operating Point (Q-point)** ของวงจร
**NPN BJT Common-Emitter** 3 ชนิดไบแอส — **Voltage Divider**, **Fixed Bias**
และ **Emitter Bias** — โดยใช้ Python Backend คำนวณจริง (ไม่ใช่ค่าฮาร์ดโค้ดใน HTML)

## ✨ Features

- เลือก **Bias Type** จาก dropdown: Voltage Divider / Fixed Bias / Emitter Bias
- ฟิลด์กรอกค่า สมการ และแผนผังวงจรเปลี่ยนตามชนิดไบแอสที่เลือก
- Python Backend คำนวณ `VB, VE, VC, VCE, IB, IC, IE`
- แปลงหน่วยตัวต้านทาน kΩ → Ω ก่อนคำนวณ
- แสดงหน่วยกำกับทุกค่า และแจ้ง **Operating Region** (Active / Saturation / Cut-off)
- Input Validation: ค่าติดลบ/ศูนย์/ไม่ใช่ตัวเลข แสดงข้อความผิดพลาดโดยไม่ทำให้เว็บล้ม
- Automated Tests ทั้งฝั่ง Engineering Logic และ Flask HTTP Route

## 🗂️ Project Structure

```
BJT DC Bias Web App/
├── app.py                  # Flask application & HTTP routes
├── dc_bias.py              # independent engineering calculations
├── templates/
│   └── index.html          # input form + DC results (Jinja)
├── static/
│   └── style.css           # responsive layout and presentation
├── tests/
│   ├── test_dc_bias.py     # unit tests for engineering logic
│   └── test_web.py         # Flask HTTP route tests
├── docs/
│   ├── design-note.md
│   ├── validation.md
│   └── reflection.md
├── requirements.txt
├── AGENTS.md
└── README.md
```

## 🚀 Getting Started

ต้องมี Python 3.10+ และ Git

```bash
# 1) สร้าง virtual environment
python -m venv .venv

# 2) เปิดใช้งาน (เลือกตามระบบปฏิบัติการ)
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# 3) ติดตั้ง dependencies
python -m pip install -r requirements.txt

# 4) รันเว็บ
python -m flask --app app run --debug
```

เปิดเบราว์เซอร์ที่ **http://127.0.0.1:5000/**

> บน Windows ที่คำสั่ง `python` ถูกบล็อกโดย Microsoft Store alias ให้ใช้
> `py` แทน เช่น `py -m venv .venv` และ `py -m flask --app app run --debug`

## 🧪 Running Tests

```bash
python -m unittest discover -s tests -v
```

## 📐 Engineering Model

แอปรองรับ 3 ชนิดไบแอส (เลือกได้จาก dropdown **Bias Type**)

### 1) Voltage Divider Bias (Approximate, I_B ≈ 0)

```
VB  = VTH = VCC × R2 / (R1 + R2)
VE  = VB − VBE
IE  = VE / RE
IC  ≈ IE
IB  = IC / β
VC  = VCC − IC · RC
VCE = VC − VE
```

> วิธี Exact (Thevenin) ที่คิดกระแสฐานโหลด divider จะให้ค่าต่างออกไปเล็กน้อย
> (VB ≈ 1.94 V, VE ≈ 1.24 V, VC ≈ 9.29 V) — เอกสาร Lab ระบุสมการ Exact ไว้
> แต่แอปนี้เลือกใช้วิธี Approximate ตามภาพตัวอย่าง

### 2) Fixed Bias

```
IB  = (VCC − VBE) / RB
IC  = β · IB
IE  = (β + 1) · IB
VB  = VBE          (VE = 0)
VC  = VCC − IC · RC
VCE = VC
```

### 3) Emitter Bias (Emitter-Stabilized)

```
IB  = (VCC − VBE) / (RB + (β + 1)·RE)
IC  = β · IB
IE  = (β + 1) · IB
VE  = IE · RE
VB  = VE + VBE
VC  = VCC − IC · RC
VCE = VC − VE
```

### ค่าอ้างอิงสำหรับตรวจสอบ

**Voltage Divider** — VCC=12 V, R1=100 kΩ, R2=22 kΩ, RC=2.2 kΩ, RE=1 kΩ, β=100, VBE=0.70 V

| ปริมาณ | ค่า |
|---|---|
| VB | ≈ 2.164 V |
| VE | ≈ 1.464 V |
| VC | ≈ 8.779 V |
| VCE | ≈ 7.315 V |
| IB / IC / IE | ≈ 14.64 µA / 1.464 mA / 1.464 mA |

**Fixed Bias** — VCC=12 V, RB=470 kΩ, RC=2.2 kΩ, β=100, VBE=0.70 V

| ปริมาณ | ค่า |
|---|---|
| VB / VE | 0.70 V / 0 V |
| VC / VCE | ≈ 6.711 V / 6.711 V |
| IB / IC / IE | ≈ 24.04 µA / 2.404 mA / 2.428 mA |

**Emitter Bias** — VCC=12 V, RB=470 kΩ, RC=2.2 kΩ, RE=1 kΩ, β=100, VBE=0.70 V

| ปริมาณ | ค่า |
|---|---|
| VB / VE | ≈ 2.699 V / 1.999 V |
| VC / VCE | ≈ 7.646 V / 5.647 V |
| IB / IC / IE | ≈ 19.79 µA / 1.979 mA / 1.999 mA |

> ผลนอกช่วง Forward-Active (Cut-off / Saturation) จะแสดง Warning และไม่ควร
> ถือว่าเป็นค่าที่เชื่อถือได้โดยไม่มีข้อจำกัดกำกับ

## 📄 License

MIT
