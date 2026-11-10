# BJT DC Bias Web App

Flask Web Application สำหรับคำนวณ **DC Operating Point (Q-point)** ของวงจร
**NPN BJT Common-Emitter แบบ Voltage-Divider Bias** โดยใช้ Python Backend
คำนวณจริง (ไม่ใช่ค่าฮาร์ดโค้ดใน HTML)

## ✨ Features

- รับค่า `VCC, R1, R2, RC, RE, β, VBE` ผ่านหน้าเว็บ
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

แอปใช้ **วิธี Approximate (I_B ≈ 0)** สำหรับวงจร Voltage-Divider Bias:

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

### ค่าอ้างอิงสำหรับตรวจสอบ

| พารามิเตอร์ | ค่า |
|---|---|
| VCC | 12 V |
| R1 / R2 | 100 kΩ / 22 kΩ |
| RC / RE | 2.2 kΩ / 1 kΩ |
| β / VBE | 100 / 0.70 V |

ผลลัพธ์ที่ควรได้ (Approximate, Forward-Active):

| ปริมาณ | ค่า |
|---|---|
| VB | ≈ 2.164 V |
| VE | ≈ 1.464 V |
| VC | ≈ 8.779 V |
| VCE | ≈ 7.315 V |
| IC | ≈ 1.464 mA |

> ผลนอกช่วง Forward-Active (Cut-off / Saturation) จะแสดง Warning และไม่ควร
> ถือว่าเป็นค่าที่เชื่อถือได้โดยไม่มีข้อจำกัดกำกับ

## 📄 License

MIT
