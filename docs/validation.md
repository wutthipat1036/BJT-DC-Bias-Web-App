# Validation — การตรวจสอบความถูกต้อง

## หน่วยที่รองรับ

- ตัวต้านทาน: Ω, kΩ, MΩ (ค่าเริ่มต้น kΩ)
- แรงดัน: V, mV (ค่าเริ่มต้น V)
- `app.py` แปลงทุกค่าเป็น SI (Ω, V) ก่อนคำนวณ

## 1) Voltage Divider Bias

### ค่าทดลองเริ่มต้น

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

## 2) Fixed Bias

พารามิเตอร์: VCC=12 V, RB=470 kΩ, RC=2.2 kΩ, β=100, VBE=0.70 V

```
IB  = (12 − 0.70) / 470k             = 24.043 µA
IC  = 100 × 24.043µ                  = 2.4043 mA
IE  = 101 × 24.043µ                  = 2.4283 mA
VB  = VBE                            = 0.70 V
VE  = 0                              = 0 V
VC  = 12 − 2.4043m × 2.2k            = 6.7106 V
VCE = VC − VE                        = 6.7106 V
```

ผลที่ได้อยู่ใน **Active Region** (VCE ≈ 6.71 V > 0.2 V)

## 3) Emitter Bias

พารามิเตอร์: VCC=12 V, RB=470 kΩ, RC=2.2 kΩ, RE=1 kΩ, β=100, VBE=0.70 V

```
IB  = (12 − 0.70) / (470k + 101×1k)  = 19.790 µA
IC  = 100 × 19.790µ                  = 1.9790 mA
IE  = 101 × 19.790µ                  = 1.9988 mA
VE  = 1.9988m × 1k                   = 1.9988 V
VB  = 1.9988 + 0.70                  = 2.6988 V
VC  = 12 − 1.9790m × 2.2k            = 7.6462 V
VCE = 7.6462 − 1.9988                = 5.6475 V
```

ผลที่ได้อยู่ใน **Active Region** (VCE ≈ 5.65 V > 0.2 V)

## ผลการทดสอบที่คาดหวัง

| รายการ | ผลที่คาด |
|---|---|
| Voltage Divider Q-point | VB≈2.164, VE≈1.464, VC≈8.779, VCE≈7.315, IC≈1.464 mA |
| Fixed Bias Q-point | VB=0.70, VE=0, VC≈6.711, VCE≈6.711, IC≈2.404 mA |
| Emitter Bias Q-point | VB≈2.699, VE≈1.999, VC≈7.646, VCE≈5.647, IC≈1.979 mA |
| R ≤ 0 | ValidationError |
| β ≤ 0 | ValidationError |
| VCC ≤ 0 | ValidationError |
| ค่าไม่ใช่ตัวเลข | ValidationError |
| VCC ≤ VBE | region = cutoff + warning |
| VCE ≤ 0.2 V | region = saturation + warning |

## Automated Tests

- `tests/test_dc_bias.py` — ตรวจสมการ, validation และ region warning
- `tests/test_web.py` — ตรวจ HTTP: GET 200, POST valid ได้ผล, POST invalid ได้ 400 + ข้อความ

## ข้อจำกัดของแบบจำลอง

- ใช้ β คงที่และ VBE คงที่ (ไม่คำนึงถึงอุณหภูมิหรือความต่างของ β จริง)
- ไม่ใช่ ngspice/SPICE — ผลนอก Forward-Active เป็นเพียงการประมาณและต้องมี Warning
