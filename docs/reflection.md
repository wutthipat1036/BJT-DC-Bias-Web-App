# Reflection — บันทึกการเรียนรู้

## สิ่งที่ได้เรียนรู้

- การแยก **engineering logic** (`dc_bias.py`) ออกจาก **web layer** (`app.py`)
  ทำให้ทดสอบสมการได้ง่ายและนำโค้ดไปใช้ซ้ำได้
- การแปลงหน่วย (kΩ → Ω) ที่ขอบเขตของระบบช่วยลดข้อผิดพลาดในสมการ
- Flask + Jinja ทำให้เห็นว่า HTML เป็นเพียง template ที่ server นำมา render
  ไม่ใช่ตัวคำนวณ
- Input validation และ warning สำคัญมาก เพราะผลนอก Forward-Active
  ไม่ควรถูกนำเสนอเป็นค่าที่เชื่อถือได้

## ปัญหาที่พบและวิธีแก้

- `python` บน Windows ถูกบล็อกโดย Microsoft Store alias → ใช้ `py` launcher แทน
- การ import `app`/`dc_bias` จากในโฟลเดอร์ `tests/` ต้องเพิ่ม project root
  เข้า `sys.path` เพื่อให้รัน `unittest discover` ได้ทุกวิธี

## แนวทางต่อยอด (สัปดาห์ถัดไป)

- เพิ่ม Bias Templates อื่น เช่น Fixed Bias, Emitter Bias
- เพิ่ม DC Load Line
- ยกระดับความสมจริงด้วย SPICE/ngspice
- เพิ่ม AC Small-Signal / Gain / Bode Plot
