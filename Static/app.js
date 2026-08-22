const COLORS = { green: "#34D399", teal: "#2DD4C8", amber: "#F5A623", red: "#EF5350", mutedDim: "#54695F", border: "#243430", muted: "#7E9A90", text: "#E7F0EC" };
let selectedId = 1;
let chart = null;

function statusColor(s) {
  if (!s.active) return COLORS.mutedDim;
  if (s.status === "em fila") return COLORS.red;
  if (s.status === "limitado" || s.status === "reservado") return COLORS.amber;
  return s.plan === "pre" ? COLORS.green : COLORS.teal;
}
function fmt(n, d = 2) { return Number(n).toFixed(d); }
async function fetchState() { const res = await fetch("/api/state"); return res.json(); }
async function toggleObj(kind, id) { await fetch(`/api/${kind}/${id}`, { method: "POST" }); render(); }

function renderLoadCard(data) {
  const loadPct = Math.min((data.total_load / data.max_capacity) * 100, 100);
  const loadColor = loadPct > 92 ? COLORS.red : loadPct > 72 ? COLORS.amber : COLORS.green;
  document.getElementById("load-value").innerHTML = `${fmt(data.total_load, 1)} <span>/ ${data.max_capacity} A</span>`;
  document.getElementById("load-value").style.color = loadColor;
  const alertEl = document.getElementById("load-alert");
  if (loadPct > 72) {
    alertEl.style.color = loadColor;
    alertEl.textContent = loadPct > 92 ? "⚠ risco de sobrecarga — limitando pós-pago" : "⚠ carga elevada";
  } else { alertEl.textContent = ""; }
  const fill = document.getElementById("bar-fill");
  fill.style.width = loadPct + "%";
  fill.style.background = `linear-gradient(90deg, ${COLORS.border}, ${loadColor})`;
  const taps = document.getElementById("taps");
  taps.innerHTML = "";
  data.stations.forEach((s) => {
    const tap = document.createElement("div");
    tap.className = "tap" + (s.id === selectedId ? " selected" : "");
    tap.style.opacity = s.active ? 1 : 0.35;
    tap.innerHTML = `<div class="line"></div><div class="dot" style="background:${statusColor(s)}"></div><div class="id mono">#${s.id}</div>`;
    tap.onclick = () => { selectedId = s.id; render(); };
    taps.appendChild(tap);
  });
}
function renderStationGrid(data) {
  const grid = document.getElementById("station-grid");
  grid.innerHTML = "";
  data.stations.forEach((s) => {
    const card = document.createElement("div");
    card.className = `station-card plan-${s.plan}` + (s.id === selectedId ? " selected" : "");
    const kw = (s.current_a * data.voltage) / 1000;
    card.innerHTML = `
      <div class="top-row">
        <div><div class="name">${s.name}</div><div class="slot mono">vaga #${s.id}</div></div>
        <button class="plug-btn" data-action="plug" data-id="${s.id}">${s.active ? "✕" : "+"}</button>
      </div>
      <div class="status-row"><span class="status-dot" style="background:${statusColor(s)}"></span><span class="status-label">${s.status}</span></div>
      <div class="kw mono">${fmt(kw)} <span>kW</span></div>
      <div class="sub">${fmt(s.energy_kwh)} kWh · R$ ${fmt(s.cost)}</div>
      <button class="plan-btn mono" data-action="plan" data-id="${s.id}">${s.plan === "pre" ? "pré-pago" : "pós-pago"} →</button>
    `;
    card.onclick = (e) => { if (e.target.dataset.action) return; selectedId = s.id; render(); };
    grid.appendChild(card);
  });
  grid.querySelectorAll('[data-action="plug"]').forEach((btn) => { btn.onclick = (e) => { e.stopPropagation(); toggleObj("toggle_plug", btn.dataset.id); }; });
  grid.querySelectorAll('[data-action="plan"]').forEach((btn) => { btn.onclick = (e) => { e.stopPropagation(); toggleObj("toggle_plan", btn.dataset.id); }; });
}
function renderFormulaCard(data) {
  const s = data.stations.find((x) => x.id === selectedId) || data.stations[0];
  const power = (s.current_a * data.voltage) / 1000;
  const price = s.plan === "pre" ? data.price_pre : data.price_pos;
  document.getElementById("formula-card").innerHTML = `
    <div class="label">Leitura em tempo real — ${s.name} <span class="mono" style="color:${COLORS.mutedDim}">#${s.id}</span></div>
    <div class="formula-row"><span class="fl">Tensão (V)</span><span class="fv mono">${data.voltage} V</span></div>
    <div class="formula-row"><span class="fl">Corrente (I)</span><span class="fv mono">${fmt(s.current_a)} A</span></div>
    <div class="hr"></div>
    <div class="formula-row big"><span class="fl">P = V · I</span><span class="fv mono">${fmt(power)} kW</span></div>
    <div class="formula-row big"><span class="fl">E = P · Δt</span><span class="fv mono">${fmt(s.energy_kwh, 3)} kWh</span></div>
    <div class="hr"></div>
    <div class="formula-row big"><span class="fl">Custo (R$ ${fmt(price)}/kWh)</span><span class="fv mono" style="color:${COLORS.green}">R$ ${fmt(s.cost)}</span></div>
  `;
}
function renderPlansCard(data) {
  document.getElementById("plans-card").innerHTML = `
    <div class="label">Planos de recarga</div>
    <div class="plan-row"><div class="plan-dot" style="background:${COLORS.green}"></div><div>
      <div class="plan-title-row"><span class="plan-title">Pré-pago</span><span class="plan-price mono">R$ ${fmt(data.price_pre)}/kWh</span></div>
      <div class="plan-desc">Energia reservada antes de carregar. Capacidade garantida no barramento — nunca é limitado por sobrecarga.</div></div></div>
    <div class="plan-row"><div class="plan-dot" style="background:${COLORS.teal}"></div><div>
      <div class="plan-title-row"><span class="plan-title">Pós-pago</span><span class="plan-price mono">R$ ${fmt(data.price_pos)}/kWh</span></div>
      <div class="plan-desc">Cobrança ao final da sessão. Mais barato, mas cede capacidade ao pré-pago quando o estacionamento se aproxima do limite.</div></div></div>
  `;
}
function renderStatsCard(data) {
  const activeCount = data.stations.filter((s) => s.active).length;
  document.getElementById("stats-card").innerHTML = `
    <div class="label">Painel de operação</div>
    <div class="stat-row"><span class="sl">Vagas ativas</span><span class="sv mono">${activeCount} / ${data.stations.length}</span></div>
    <div class="stat-row"><span class="sl">Energia entregue</span><span class="sv mono">${fmt(data.total_energy)} kWh</span></div>
    <div class="stat-row"><span class="sl">Eventos de sobrecarga evitados</span><span class="sv mono" style="color:${data.overload_events > 0 ? COLORS.amber : COLORS.text}">${data.overload_events}</span></div>
  `;
}
function renderChart(data) {
  document.getElementById("total-revenue").textContent = `R$ ${fmt(data.total_revenue)}`;
  const labels = data.history.map((h) => h.t);
  const pre = data.history.map((h) => h.pre);
  const pos = data.history.map((h) => h.pos);
  if (!chart) {
    const ctx = document.getElementById("revenue-chart").getContext("2d");
    chart = new Chart(ctx, {
      type: "line",
      data: { labels, datasets: [
        { label: "pré-pago (R$)", data: pre, borderColor: COLORS.green, backgroundColor: "rgba(52,211,153,0.2)", fill: true, tension: 0.3, pointRadius: 0 },
        { label: "pós-pago (R$)", data: pos, borderColor: COLORS.teal, backgroundColor: "rgba(45,212,200,0.2)", fill: true, tension: 0.3, pointRadius: 0 },
      ]},
      options: { responsive: true, animation: false, interaction: { mode: "index", intersect: false },
        scales: { x: { ticks: { color: COLORS.mutedDim, font: { size: 10 } }, grid: { color: COLORS.border } },
                  y: { stacked: true, ticks: { color: COLORS.mutedDim, font: { size: 10 } }, grid: { color: COLORS.border } } },
        plugins: { legend: { labels: { color: COLORS.muted, font: { size: 11 } } } } },
    });
  } else {
    chart.data.labels = labels; chart.data.datasets[0].data = pre; chart.data.datasets[1].data = pos; chart.update("none");
  }
}
async function render() {
  const data = await fetchState();
  renderLoadCard(data); renderStationGrid(data); renderFormulaCard(data);
  renderPlansCard(data); renderStatsCard(data); renderChart(data);
}
render();
setInterval(render, 1500);
