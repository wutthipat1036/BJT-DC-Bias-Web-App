# BJT DC Bias Web App

เว็บแอปสำหรับคำนวณและวิเคราะห์ **DC Bias** ของทรานซิสเตอร์ BJT (Bipolar Junction Transistor)
ช่วยให้นักศึกษาและวิศวกรelectronics หาจุดทำงาน (Q-point) ของวงจรได้อย่างรวดเร็วผ่านเบราว์เซอร์

## ✨ Features

- คำนวณ Q-point (I_C, V_CE) ของวงจร Fixed Bias และ Voltage Divider Bias
- แสดงผลลัพธ์แบบเรียลไทม์เมื่อปรับค่าตัวต้านทานและแรงดัน
- รองรับการเลือกชนิดทรานซิสเตอร์ (NPN / PNP)
- ใช้งานได้บนเบราว์เซอร์โดยไม่ต้องติดตั้งเพิ่ม

## 🚀 Getting Started

เปิดไฟล์ `index.html` ในเบราว์เซอร์ได้โดยตรง หรือรัน local server:

```bash
# ตัวอย่างด้วย Python
python -m http.server 8000
```

แล้วเปิด http://localhost:8000

## 🛠️ Tech Stack

- HTML5
- CSS3
- JavaScript (Vanilla)

## 📁 Project Structure

```
BJT DC Bias Web App/
├── index.html      # หน้าหลักของแอป
├── css/
│   └── style.css   # สไตล์
├── js/
│   └── app.js      # ตรรกะการคำนวณ
└── README.md
```

## 📐 สูตรที่ใช้

**Fixed Bias**
```
I_B = (V_CC - V_BE) / R_B
I_C = β * I_B
V_CE = V_CC - I_C * R_C
```

**Voltage Divider Bias**
```
V_B  = V_CC * R2 / (R1 + R2)
V_E  = V_B - V_BE
I_E  = V_E / R_E
I_C  ≈ I_E
V_CE = V_CC - I_C * (R_C + R_E)
```

## 📄 License

MIT
