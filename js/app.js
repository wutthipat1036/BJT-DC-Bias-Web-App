// BJT DC Bias Calculator
// หมายเหตุ: ตัวต้านทานมีหน่วย kΩ และแรงดันมีหน่วย V
// ทำให้กระแสที่คำนวณได้ออกมาเป็น mA โดยอัตโนมัติ (V / kΩ = mA)

const els = {
  circuitType: document.getElementById("circuitType"),
  transistorType: document.getElementById("transistorType"),
  vcc: document.getElementById("vcc"),
  vbe: document.getElementById("vbe"),
  beta: document.getElementById("beta"),
  rb: document.getElementById("rb"),
  rc: document.getElementById("rc"),
  r1: document.getElementById("r1"),
  r2: document.getElementById("r2"),
  rc2: document.getElementById("rc2"),
  re: document.getElementById("re"),
};

const fixedFields = document.querySelector(".fixed-fields");
const dividerFields = document.querySelector(".divider-fields");

const out = {
  status: document.getElementById("status"),
  ib: document.getElementById("outIb"),
  ic: document.getElementById("outIc"),
  ie: document.getElementById("outIe"),
  vce: document.getElementById("outVce"),
  vb: document.getElementById("outVb"),
  ve: document.getElementById("outVe"),
  note: document.getElementById("note"),
};

const STATUS_LABEL = {
  active: "Active Region ✅",
  saturation: "Saturation ⚠️",
  cutoff: "Cut-off ⚠️",
  invalid: "ข้อมูลไม่ถูกต้อง",
};

function num(el) {
  const v = parseFloat(el.value);
  return Number.isFinite(v) ? v : NaN;
}

function fmt(value, unit) {
  if (!Number.isFinite(value)) return "—";
  return `${value.toFixed(3)} ${unit}`;
}

function toggleFields() {
  const isFixed = els.circuitType.value === "fixed";
  fixedFields.classList.toggle("hidden", !isFixed);
  dividerFields.classList.toggle("hidden", isFixed);
}

function clearOutputs() {
  out.ib.textContent =
    out.ic.textContent =
    out.ie.textContent =
    out.vce.textContent =
    out.vb.textContent =
    out.ve.textContent =
      "—";
}

function setStatus(region, noteText) {
  out.status.className = "status-badge " + region;
  out.status.textContent = STATUS_LABEL[region] || "—";
  out.note.textContent = noteText || "";
}

function compute() {
  const vcc = num(els.vcc);
  const vbe = Math.abs(num(els.vbe));
  const beta = num(els.beta);
  const isPnp = els.transistorType.value === "pnp";

  if (!Number.isFinite(vcc) || !Number.isFinite(beta) || beta <= 0) {
    clearOutputs();
    setStatus("invalid", "กรุณากรอกค่า V_CC และ β ให้ถูกต้อง");
    return;
  }

  let ib, ic, ie, vce, vb, ve;
  let invalidNote = "";

  if (els.circuitType.value === "fixed") {
    const rb = num(els.rb);
    const rc = num(els.rc);

    if (!Number.isFinite(rb) || rb <= 0 || !Number.isFinite(rc) || rc < 0) {
      clearOutputs();
      setStatus("invalid", "กรุณากรอก R_B (มากกว่า 0) และ R_C ให้ถูกต้อง");
      return;
    }

    ib = (vcc - vbe) / rb; // mA
    ic = beta * ib;
    ie = ic + ib;
    vce = vcc - ic * rc;
    vb = vbe;
    ve = 0;
  } else {
    const r1 = num(els.r1);
    const r2 = num(els.r2);
    const rc = num(els.rc2);
    const re = num(els.re);

    if (
      !Number.isFinite(r1) ||
      !Number.isFinite(r2) ||
      r1 + r2 <= 0 ||
      !Number.isFinite(re) ||
      re <= 0
    ) {
      clearOutputs();
      setStatus("invalid", "กรุณากรอก R1, R2 และ R_E ให้ถูกต้อง");
      return;
    }

    vb = (vcc * r2) / (r1 + r2);
    ve = vb - vbe;
    ie = ve / re;
    ic = (ie * beta) / (beta + 1);
    ib = ic / beta;
    vce = vcc - ic * rc - ie * re;
  }

  // --- ตรวจสอบย่านการทำงาน ---
  let region = "active";
  let noteText = "";

  if (!Number.isFinite(ib) || !Number.isFinite(ic) || ib <= 0 || ic <= 0) {
    region = "cutoff";
    noteText = "กระแสฐานเป็นลบหรือศูนย์ ทรานซิสเตอร์อยู่ในช่วง Cut-off";
  } else if (vce <= 0.2) {
    region = "saturation";
    noteText = "V_CE ต่ำมาก (≤ 0.2 V) ทรานซิสเตอร์อิ่มตัว (Saturation)";
  }

  if (isPnp) {
    noteText = (noteText ? noteText + " " : "") +
      "แสดงผลเป็นค่าขนาดสัมบูรณ์ (absolute) สำหรับ PNP — ขั้วแรงดัน/กระแสตรงข้ามกับ NPN";
  }

  setStatus(region, noteText);

  out.ib.textContent = fmt(ib, "mA");
  out.ic.textContent = fmt(ic, "mA");
  out.ie.textContent = fmt(ie, "mA");
  out.vce.textContent = fmt(vce, "V");
  out.vb.textContent = fmt(vb, "V");
  out.ve.textContent = fmt(ve, "V");
}

// --- Event wiring ---
els.circuitType.addEventListener("change", () => {
  toggleFields();
  compute();
});

document.querySelectorAll("input, select").forEach((el) => {
  el.addEventListener("input", compute);
});

toggleFields();
compute();
