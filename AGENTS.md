# AGENTS.md — AI Coding Conventions

แนวทางสำหรับ AI agent และผู้พัฒนาที่ทำงานกับโปรเจกต์นี้

## Architecture Rules

- **แยกชั้นให้ชัดเจน**: `dc_bias.py` เป็น pure engineering logic ห้าม import
  Flask / HTML / HTTP สิ่งใดทั้งสิ้น
- `app.py` รับผิดชอบ HTTP, การแปลงหน่วย (kΩ → Ω) และการ render เท่านั้น
- `templates/index.html` แสดงผลผ่าน Jinja ห้ามฝังสมการฟิสิกส์ลงใน template
- `static/style.css` ดูแลเฉพาะหน้าตา

## Units

- ภายใน `dc_bias.py` ใช้หน่วย SI: Ω, V, A
- UI รับตัวต้านทานเป็น kΩ แล้วแปลงเป็น Ω ที่ `app.py` ก่อนเรียก logic
- แสดงผล IC/IE เป็น mA และ IB เป็น µA พร้อมหน่วยกำกับเสมอ

## Testing

- ทุกการเปลี่ยนสมการต้องมี/ปรับ unit test ใน `tests/test_dc_bias.py`
- การเปลี่ยน route หรือ validation ต้องมี test ใน `tests/test_web.py`
- รันเทสต์ก่อน commit ทุกครั้ง:

```bash
python -m unittest discover -s tests -v
```

## Style

- Python: ใช้ type hints, docstring, `from __future__ import annotations`
- ตั้งชื่อตัวแปรให้ตรงกับสัญลักษณ์วงจร (vcc, r1, beta, vbe, ...)
- ข้อความแจ้งผู้ใช้ (validation/warning) เป็นภาษาไทยที่อ่านเข้าใจได้

## Do Not

- ห้าม commit `.venv/`, `__pycache__/`, `.env` หรือ secrets
- ห้ามฮาร์ดโค้ดผลลัพธ์ DC Bias ลงใน HTML
- ห้ามรายงานผลนอก Forward-Active โดยไม่มี warning
