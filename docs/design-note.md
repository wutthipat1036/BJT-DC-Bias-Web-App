# Design Note — Lab 02 BJT DC Bias Web App

## เป้าหมาย

สร้าง Web Application ที่รันบน Local Server ด้วย Flask ซึ่งรับค่าชิ้นส่วนของวงจร
BJT Common-Emitter แล้วคำนวณ DC Operating Point ด้วย Python Backend จริง
รองรับ 3 ชนิดไบแอส: Voltage Divider, Fixed Bias และ Emitter Bias

## ขอบเขต (Week 2)

- **ทำ**: Voltage-Divider Bias, Fixed Bias, Emitter Bias, NPN, Forward-Active approximation
- **ยังไม่ทำ**: AC analysis, Transient, Bode plot, Signal Generator, FET, SPICE solver

## การแยกความรับผิดชอบ

| ไฟล์ | หน้าที่ |
|---|---|
| `app.py` | HTTP routes, unit conversion (kΩ → Ω), bias-type dispatch, render template |
| `dc_bias.py` | สมการวิศวกรรมล้วน ๆ (ทั้ง 3 ชนิดไบแอส), validation, region detection |
| `templates/index.html` | ฟอร์มกรอกค่า + แผนผังวงจร + ตารางผลลัพธ์ (Jinja + vanilla JS) |
| `static/style.css` | หน้าตา/เลย์เอาต์ |
| `tests/` | unit test + HTTP test |

## Data Flow

```
Browser (form POST)
   → app.py  (แปลง kΩ → Ω, เรียก logic)
   → dc_bias.py (คำนวณ Q-point + ตรวจ region)
   → render_template(index.html) ส่ง HTML กลับ Browser
```

## การตัดสินใจสำคัญ

1. **แยก logic ออกจาก web** เพื่อให้ทดสอบสมการได้โดยไม่ต้องมี HTTP
2. **กรอกตัวต้านทานเป็น kΩ** เพราะค่าจริงในวงจรไบแอสอยู่ในหลัก kΩ–MΩ
3. **แสดง Warning** เมื่ออยู่นอก Forward-Active เพื่อไม่ให้เข้าใจผิดว่าเป็นค่าจริง
4. **Validation ที่ boundary** ทั้งใน `app.py` (แปลงตัวเลข) และ `dc_bias.py` (ค่าทางฟิสิกส์)
5. **ใช้วิธี Approximate (I_B ≈ 0)** — ให้ `V_B = V_TH` โดยไม่คิดกระแสฐานโหลด divider
   เพื่อให้ผลสอดคล้องกับภาพตัวอย่าง/แนวการสอนของ Lab
