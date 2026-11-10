# Validation — การตรวจสอบความถูกต้อง

## ค่าทดลองเริ่มต้น

| พารามิเตอร์ | ค่า |
|---|---|
| VCC | 12 V |
| R1 | 100 kΩ |
| R2 | 22 kΩ |
| RC | 2.2 kΩ |
| RE | 1 kΩ |
| β | 100 |
| VBE | 0.70 V |

## การคำนวณอ้างอิงด้วยมือ (วิธี Approximate, I_B ≈ 0)

```
VB  = 12 × 22 / (100 + 22)          = 2.1639 V
VE  = 2.1639 − 0.70                 = 1.4639 V
IE  = 1.4639 / 1k                   = 1.4639 mA
IC  ≈ IE                            = 1.4639 mA
IB  = 1.4639m / 100                 = 14.64 µA
VC  = 12 − 1.4639m × 2.2k           = 8.7793 V
VCE = 8.7793 − 1.4639               = 7.3154 V
```

ผลที่ได้อยู่ใน **Active Region** (VCE ≈ 7.32 V > 0.2 V และ VTH > VBE)

> หมายเหตุ: วิธี Exact (Thevenin) ที่คิดกระแสฐานจะได้ VB≈1.942, VE≈1.242,
> VC≈9.294, VCE≈8.052, IC≈1.230 mA — แอปนี้เลือกใช้วิธี Approximate

## ผลการทดสอบที่คาดหวัง

| รายการ | ผลที่คาด |
|---|---|
| Reference Q-point | VB≈2.164, VE≈1.464, VC≈8.779, VCE≈7.315, IC≈1.464 mA |
| R ≤ 0 | ValidationError |
| β ≤ 0 | ValidationError |
| VCC ≤ 0 | ValidationError |
| ค่าไม่ใช่ตัวเลข | ValidationError |
| VTH ≤ VBE | region = cutoff + warning |
| VCE ≤ 0.2 V | region = saturation + warning |

## Automated Tests

- `tests/test_dc_bias.py` — ตรวจสมการ, validation และ region warning
- `tests/test_web.py` — ตรวจ HTTP: GET 200, POST valid ได้ผล, POST invalid ได้ 400 + ข้อความ

## ข้อจำกัดของแบบจำลอง

- ใช้ β คงที่และ VBE คงที่ (ไม่คำนึงถึงอุณหภูมิหรือความต่างของ β จริง)
- ไม่ใช่ ngspice/SPICE — ผลนอก Forward-Active เป็นเพียงการประมาณและต้องมี Warning
