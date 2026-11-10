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

## การคำนวณอ้างอิงด้วยมือ

```
VTH = 12 × 22 / (100 + 22)          = 2.1639 V
RTH = 100 × 22 / (100 + 22)         = 18.0328 kΩ
IB  = (2.1639 − 0.70) / (18.0328k + 101×1k)
    = 1.4639 / 119032.8             = 12.30 µA
IC  = 100 × 12.30µ                  = 1.230 mA
IE  = 101 × 12.30µ                  = 1.242 mA
VE  = 1.242m × 1k                   = 1.242 V
VB  = 1.242 + 0.70                  = 1.942 V
VC  = 12 − 1.230m × 2.2k            = 9.294 V
VCE = 9.294 − 1.242                 = 8.052 V
```

ผลที่ได้อยู่ใน **Active Region** (VCE ≈ 8.05 V > 0.2 V และ VTH > VBE)

## ผลการทดสอบที่คาดหวัง

| รายการ | ผลที่คาด |
|---|---|
| Reference Q-point | VB≈1.942, VE≈1.242, VC≈9.294, VCE≈8.052, IC≈1.230 mA |
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
