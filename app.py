import random
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except ImportError:
    HAS_AUTOREFRESH = False

# ---------------------------------------------------------------------------
# Config / tokens
# ---------------------------------------------------------------------------
st.set_page_config(page_title="ReCarga — Dashboard", page_icon="⚡", layout="wide")

C = dict(
    bg="#0B1210", panel="#121C19", panelAlt="#17231F",
    border="#243430", borderBright="#33473F",
    text="#E7F0EC", muted="#7E9A90", mutedDim="#54695F",
    green="#34D399", teal="#2DD4C8", amber="#F5A623", red="#EF5350",
)

VOLTAGE = 230
MAX_CAPACITY_A = 40
PRICE_PRE = 1.35
PRICE_POS = 0.98
TICK_SECONDS = 1.5
TICK_HOURS = TICK_SECONDS / 3600

CAR_NAMES = ["Onix EV", "HB20 e", "Kwid Volt", "Compass e", "Fastback e", "Corolla e+"]

STATUS_COLOR = {
    "livre": C["mutedDim"], "em fila": C["red"], "limitado": C["amber"],
    "reservado": C["amber"], "carregando_pre": C["green"], "carregando_pos": C["teal"],
}


def status_color(s):
    if not s["active"]:
        return C["mutedDim"]
    if s["status"] in ("em fila",):
        return C["red"]
    if s["status"] in ("limitado", "reservado"):
        return C["amber"]
    return C["green"] if s["plan"] == "pre" else C["teal"]


def make_station(i, plan, active):
    return dict(
        id=i, name=CAR_NAMES[(i - 1) % len(CAR_NAMES)], plan=plan, active=active,
        target_a=16 if plan == "pre" else 10, current_a=0.0,
        status="carregando" if active else "livre",
        energy_kwh=0.0, cost=0.0,
    )


# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------
if "stations" not in st.session_state:
    st.session_state.stations = [
        make_station(1, "pre", True), make_station(2, "pos", True),
        make_station(3, "pos", True), make_station(4, "pre", True),
        make_station(5, "pos", False), make_station(6, "pre", False),
    ]
if "history" not in st.session_state:
    st.session_state.history = [dict(t=0, pre=0.0, pos=0.0, load=0.0)]
if "selected_id" not in st.session_state:
    st.session_state.selected_id = 1
if "overload_events" not in st.session_state:
    st.session_state.overload_events = 0
if "overload_flag" not in st.session_state:
    st.session_state.overload_flag = False
if "last_tick" not in st.session_state:
    st.session_state.last_tick = -1


def step():
    stations = st.session_state.stations
    active = [s for s in stations if s["active"]]
    pre = [s for s in active if s["plan"] == "pre"]
    pos = [s for s in active if s["plan"] == "pos"]

    pre_target_total = sum(s["target_a"] for s in pre)
    pre_scale = MAX_CAPACITY_A / pre_target_total if pre_target_total > MAX_CAPACITY_A else 1
    reserved = min(pre_target_total, MAX_CAPACITY_A)
    remaining = max(MAX_CAPACITY_A - reserved, 0)

    pos_target_total = sum(s["target_a"] for s in pos)
    pos_scale = min(remaining / pos_target_total, 1) if pos_target_total > 0 else 1

    is_overloaded = pos_target_total > remaining + 0.01
    if is_overloaded and not st.session_state.overload_flag:
        st.session_state.overload_events += 1
    st.session_state.overload_flag = is_overloaded

    for s in stations:
        if not s["active"]:
            s["current_a"] = 0.0
            s["status"] = "livre"
            continue
        jitter = random.uniform(0.9, 1.1)
        if s["plan"] == "pre":
            cur = s["target_a"] * pre_scale * jitter
            power = cur * VOLTAGE / 1000
            dE = power * TICK_HOURS
            s["current_a"] = cur
            s["status"] = "reservado" if pre_scale < 0.999 else "carregando"
            s["energy_kwh"] += dE
            s["cost"] += dE * PRICE_PRE
        else:
            cur = s["target_a"] * pos_scale * jitter
            power = cur * VOLTAGE / 1000
            dE = power * TICK_HOURS
            status = "carregando"
            if pos_scale <= 0.01:
                status = "em fila"
            elif pos_scale < 0.85:
                status = "limitado"
            s["current_a"] = cur
            s["status"] = status
            s["energy_kwh"] += dE
            s["cost"] += dE * PRICE_POS

    pre_revenue = sum(s["cost"] for s in stations if s["plan"] == "pre")
    pos_revenue = sum(s["cost"] for s in stations if s["plan"] == "pos")
    load = sum(s["current_a"] for s in stations)
    hist = st.session_state.history
    hist.append(dict(t=len(hist), pre=round(pre_revenue, 2), pos=round(pos_revenue, 2), load=round(load, 1)))
    st.session_state.history = hist[-40:]


def toggle_plan(i):
    for s in st.session_state.stations:
        if s["id"] == i:
            s["plan"] = "pos" if s["plan"] == "pre" else "pre"
            s["target_a"] = 10 if s["plan"] == "pos" else 16


def toggle_plug(i):
    for s in st.session_state.stations:
        if s["id"] == i:
            s["active"] = not s["active"]
            s["current_a"] = 0.0
            s["status"] = "carregando" if s["active"] else "livre"


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background: {C['bg']}; color: {C['text']}; }}
h1,h2,h3 {{ font-family: 'Space Grotesk', sans-serif !important; }}
.mono {{ font-family: 'IBM Plex Mono', monospace; }}
div[data-testid="stVerticalBlockBorderWrapper"] > div {{
    background: {C['panel']}; border: 1px solid {C['border']}; border-radius: 12px;
}}
.stButton>button {{
    background: {C['panelAlt']}; color: {C['text']}; border: 1px solid {C['border']};
    border-radius: 7px; font-family: 'IBM Plex Mono', monospace; font-size: 12px;
}}
.stButton>button:hover {{ border-color: {C['borderBright']}; color: {C['green']}; }}
.chip {{ display:inline-flex; align-items:center; gap:6px; border:1px solid {C['border']};
    background:{C['panel']}; padding:4px 10px; border-radius:8px; font-size:12px; color:{C['muted']}; margin-right:6px;}}
.badge {{ font-size: 11px; padding: 2px 8px; border-radius: 20px; border: 1px solid {C['border']}; color:{C['muted']}; font-family:'IBM Plex Mono', monospace;}}
hr {{ border-color: {C['border']}; }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Autorefresh / manual tick control
# ---------------------------------------------------------------------------
st.markdown("### ⚡ ReCarga <span class='badge'>protótipo v0.3</span>", unsafe_allow_html=True)
st.caption("Sistema de recarga veicular com controle de sobrecarga · projeto acadêmico em parceria com GoodWe")
st.markdown(
    "<span class='chip'>📡 Sensor de efeito Hall</span>"
    "<span class='chip'>🧩 ESP32</span>"
    "<span class='chip'>🔳 QR Code</span>",
    unsafe_allow_html=True,
)

top_l, top_r = st.columns([3, 1])
with top_r:
    auto = st.toggle("Simulação automática", value=HAS_AUTOREFRESH, disabled=not HAS_AUTOREFRESH)
    if not HAS_AUTOREFRESH:
        st.caption("Instale `streamlit-autorefresh` para rodar sozinho, ou avance manualmente:")
        if st.button("▶ Avançar 1 tick"):
            step()

if HAS_AUTOREFRESH and auto:
    count = st_autorefresh(interval=int(TICK_SECONDS * 1000), key="tick_counter")
    if count != st.session_state.last_tick:
        st.session_state.last_tick = count
        step()

st.divider()

stations = st.session_state.stations
total_load = sum(s["current_a"] for s in stations)
load_pct = min(total_load / MAX_CAPACITY_A * 100, 100)
total_revenue = sum(s["cost"] for s in stations)
total_energy = sum(s["energy_kwh"] for s in stations)
load_color = C["red"] if load_pct > 92 else (C["amber"] if load_pct > 72 else C["green"])

left, right = st.columns([1.55, 1])

# ---------------------------------------------------------------------------
# LEFT COLUMN
# ---------------------------------------------------------------------------
with left:
    with st.container(border=True):
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown("<span style='font-size:12px;color:%s;text-transform:uppercase;letter-spacing:1px;'>Barramento do estacionamento</span>" % C["muted"], unsafe_allow_html=True)
            st.markdown(
                f"<div class='mono' style='font-size:30px;font-weight:600;color:{load_color};'>"
                f"{total_load:.1f}<span style='font-size:15px;color:{C['muted']};'> / {MAX_CAPACITY_A} A</span></div>",
                unsafe_allow_html=True,
            )
        with c2:
            if load_pct > 72:
                msg = "risco de sobrecarga — limitando pós-pago" if load_pct > 92 else "carga elevada"
                st.markdown(f"<div class='mono' style='color:{load_color};font-size:12px;text-align:right;padding-top:14px;'>⚠ {msg}</div>", unsafe_allow_html=True)

        # trace bar
        st.markdown(
            f"""<div style='position:relative;height:10px;background:{C['bg']};border-radius:6px;
            overflow:hidden;border:1px solid {C['border']};margin-top:8px;'>
            <div style='position:absolute;left:0;top:0;bottom:0;width:{load_pct}%;
            background:linear-gradient(90deg,{C['border']},{load_color});'></div></div>""",
            unsafe_allow_html=True,
        )

        # station taps
        tap_cols = st.columns(len(stations))
        for col, s in zip(tap_cols, stations):
            dot = status_color(s)
            col.markdown(
                f"<div style='text-align:center;opacity:{1 if s['active'] else 0.35};'>"
                f"<div style='width:9px;height:9px;border-radius:999px;background:{dot};margin:0 auto;'></div>"
                f"<div class='mono' style='font-size:10px;color:{C['mutedDim']};margin-top:3px;'>#{s['id']}</div></div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            f"<div style='margin-top:10px;font-size:11px;color:{C['muted']};'>"
            f"🟢 pré-pago garantido &nbsp;&nbsp; 🔵 pós-pago normal &nbsp;&nbsp; 🟡 pós-pago limitado &nbsp;&nbsp; 🔴 pós-pago em fila</div>",
            unsafe_allow_html=True,
        )

    st.write("")

    # Station grid
    grid_cols = st.columns(3)
    for idx, s in enumerate(stations):
        with grid_cols[idx % 3]:
            with st.container(border=True):
                dot = status_color(s)
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;'>"
                    f"<b style='font-family:Space Grotesk;font-size:13px;'>{s['name']}</b>"
                    f"<span class='mono' style='font-size:10px;color:{C['mutedDim']};'>vaga #{s['id']}</span></div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='margin:6px 0;'><span style='color:{dot};'>●</span> "
                    f"<span style='font-size:11px;color:{C['muted']};'>{s['status']}</span></div>",
                    unsafe_allow_html=True,
                )
                power_kw = s["current_a"] * VOLTAGE / 1000
                st.markdown(
                    f"<div class='mono' style='font-size:18px;font-weight:600;'>{power_kw:.2f} "
                    f"<span style='font-size:11px;color:{C['muted']};font-weight:400;'>kW</span></div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='font-size:11px;color:{C['muted']};'>{s['energy_kwh']:.2f} kWh · R$ {s['cost']:.2f}</div>",
                    unsafe_allow_html=True,
                )
                b1, b2, b3 = st.columns(3)
                if b1.button("🔌", key=f"plug_{s['id']}", help="Conectar/desconectar"):
                    toggle_plug(s["id"])
                    st.rerun()
                if b2.button(s["plan"], key=f"plan_{s['id']}", help="Trocar plano"):
                    toggle_plan(s["id"])
                    st.rerun()
                if b3.button("→", key=f"sel_{s['id']}", help="Ver fórmulas"):
                    st.session_state.selected_id = s["id"]
                    st.rerun()

    st.write("")

    # Chart
    with st.container(border=True):
        st.markdown(f"<span style='font-size:12px;color:{C['muted']};text-transform:uppercase;letter-spacing:1px;'>Receita acumulada</span> "
                     f"<span class='mono' style='float:right;'>R$ {total_revenue:.2f}</span>", unsafe_allow_html=True)
        df = pd.DataFrame(st.session_state.history)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["t"], y=df["pre"], stackgroup="one", name="pré-pago (R$)",
                                  line=dict(color=C["green"]), fillcolor="rgba(52,211,153,0.25)"))
        fig.add_trace(go.Scatter(x=df["t"], y=df["pos"], stackgroup="one", name="pós-pago (R$)",
                                  line=dict(color=C["teal"]), fillcolor="rgba(45,212,200,0.25)"))
        fig.update_layout(
            height=230, margin=dict(l=0, r=0, t=20, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=C["muted"], family="IBM Plex Mono"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(gridcolor=C["border"], showgrid=True, zeroline=False),
            yaxis=dict(gridcolor=C["border"], showgrid=True, zeroline=False),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ---------------------------------------------------------------------------
# RIGHT COLUMN
# ---------------------------------------------------------------------------
with right:
    selected = next((s for s in stations if s["id"] == st.session_state.selected_id), stations[0])

    with st.container(border=True):
        st.markdown(
            f"<span style='font-size:12px;color:{C['muted']};text-transform:uppercase;letter-spacing:1px;'>"
            f"Leitura em tempo real — {selected['name']} <span style='color:{C['mutedDim']};'>#{selected['id']}</span></span>",
            unsafe_allow_html=True,
        )

        def row(label, value, big=False, color=None):
            col = color or (C["text"] if big else C["muted"])
            size = 16 if big else 13
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;padding:5px 0;'>"
                f"<span style='font-size:13px;color:{C['muted']};'>{label}</span>"
                f"<span class='mono' style='font-size:{size}px;font-weight:{600 if big else 400};color:{col};'>{value}</span></div>",
                unsafe_allow_html=True,
            )

        row("Tensão (V)", f"{VOLTAGE} V")
        row("Corrente (I)", f"{selected['current_a']:.2f} A")
        st.markdown(f"<hr style='margin:8px 0;border-color:{C['border']};'>", unsafe_allow_html=True)
        row("P = V · I", f"{selected['current_a'] * VOLTAGE / 1000:.2f} kW", big=True)
        row("E = P · Δt", f"{selected['energy_kwh']:.3f} kWh", big=True)
        st.markdown(f"<hr style='margin:8px 0;border-color:{C['border']};'>", unsafe_allow_html=True)
        price = PRICE_PRE if selected["plan"] == "pre" else PRICE_POS
        row(f"Custo (R$ {price:.2f}/kWh)", f"R$ {selected['cost']:.2f}", big=True, color=C["green"])

    st.write("")

    with st.container(border=True):
        st.markdown(f"<span style='font-size:12px;color:{C['muted']};text-transform:uppercase;letter-spacing:1px;'>Planos de recarga</span>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='margin-top:10px;'><b style='font-family:Space Grotesk;color:{C['green']};'>● Pré-pago</b> "
            f"<span class='mono' style='float:right;color:{C['muted']};'>R$ {PRICE_PRE:.2f}/kWh</span>"
            f"<div style='font-size:12px;color:{C['muted']};margin-top:4px;'>Energia reservada antes de carregar. Capacidade garantida no barramento — nunca é limitado por sobrecarga.</div></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='margin-top:14px;'><b style='font-family:Space Grotesk;color:{C['teal']};'>● Pós-pago</b> "
            f"<span class='mono' style='float:right;color:{C['muted']};'>R$ {PRICE_POS:.2f}/kWh</span>"
            f"<div style='font-size:12px;color:{C['muted']};margin-top:4px;'>Cobrança ao final da sessão. Mais barato, mas cede capacidade ao pré-pago quando o estacionamento se aproxima do limite.</div></div>",
            unsafe_allow_html=True,
        )

    st.write("")

    with st.container(border=True):
        st.markdown(f"<span style='font-size:12px;color:{C['muted']};text-transform:uppercase;letter-spacing:1px;'>Painel de operação</span>", unsafe_allow_html=True)
        active_count = sum(1 for s in stations if s["active"])
        st.markdown(
            f"<div style='display:flex;justify-content:space-between;padding:5px 0;'><span style='font-size:13px;color:{C['muted']};'>Vagas ativas</span>"
            f"<span class='mono' style='font-size:13px;'>{active_count} / {len(stations)}</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='display:flex;justify-content:space-between;padding:5px 0;'><span style='font-size:13px;color:{C['muted']};'>Energia entregue</span>"
            f"<span class='mono' style='font-size:13px;'>{total_energy:.2f} kWh</span></div>",
            unsafe_allow_html=True,
        )
        ov_color = C["amber"] if st.session_state.overload_events > 0 else C["text"]
        st.markdown(
            f"<div style='display:flex;justify-content:space-between;padding:5px 0;'><span style='font-size:13px;color:{C['muted']};'>Eventos de sobrecarga evitados</span>"
            f"<span class='mono' style='font-size:13px;color:{ov_color};'>{st.session_state.overload_events}</span></div>",
            unsafe_allow_html=True,
        )

    st.caption(
        "Simulação de referência — cada vaga representa um carregador com sensor de efeito Hall lendo a "
        "corrente (I); o ESP32 envia a leitura por Bluetooth ao app, que calcula potência, energia e custo em tempo real."
    )
