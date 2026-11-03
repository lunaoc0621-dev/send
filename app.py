import paho.mqtt.client as paho
import time
import streamlit as st
import json
import platform

st.set_page_config(
    page_title="MQTT Control",
    page_icon="🎛️",
    layout="centered",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;500;600;700&family=Share+Tech+Mono&display=swap');

    :root {
        --void: #050A14;
        --panel: #0A1628;
        --panel-2: #0F2038;
        --grid: rgba(0, 229, 255, 0.07);
        --edge: #17405C;
        --text: #D6F1FF;
        --text-dim: #6F93AD;
        --cyan: #00E5FF;
        --cyan-glow: rgba(0, 229, 255, 0.45);
        --magenta: #FF2E88;
        --magenta-glow: rgba(255, 46, 136, 0.45);
        --bevel: 14px;
    }

    html, body, [class*="css"], .stApp { font-family: 'Chakra Petch', system-ui, sans-serif; }

    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: var(--void) !important;
        background-image:
            linear-gradient(var(--grid) 1px, transparent 1px),
            linear-gradient(90deg, var(--grid) 1px, transparent 1px),
            radial-gradient(ellipse at 50% -10%, rgba(0,229,255,0.14), transparent 55%);
        background-size: 36px 36px, 36px 36px, 100% 100%;
        color: var(--text) !important;
    }
    .block-container { padding-top: 2rem; max-width: 760px; }

    header[data-testid="stHeader"] { background: transparent !important; }
    header[data-testid="stHeader"] * { color: var(--cyan) !important; fill: var(--cyan) !important; }

    .stApp p, .stApp label, .stApp li, .stApp h2, .stApp h3,
    [data-testid="stWidgetLabel"] p { color: var(--text) !important; }

    /* ---------- HERO ---------- */
    .hero {
        position: relative;
        background: linear-gradient(135deg, var(--panel-2), var(--panel));
        border: 1px solid var(--cyan);
        clip-path: polygon(0 0, calc(100% - 28px) 0, 100% 28px, 100% 100%, 28px 100%, 0 calc(100% - 28px));
        padding: 1.6rem 1.9rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 0 28px var(--cyan-glow), inset 0 0 40px rgba(0,229,255,0.06);
    }
    .hero::before {
        content: "";
        position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
        background: var(--cyan);
        box-shadow: 0 0 14px var(--cyan);
    }
    .stApp .hero h1 {
        color: var(--cyan) !important;
        font-size: 1.9rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        margin: 0 0 0.3rem 0;
        padding: 0;
        text-shadow: 0 0 16px var(--cyan-glow);
    }
    .stApp .hero p { color: var(--text-dim) !important; margin: 0 0 1rem 0; font-size: 0.95rem; }
    .chips { display: flex; flex-wrap: wrap; gap: 0.5rem; }
    .stApp .chip {
        background: rgba(0,229,255,0.06);
        border: 1px solid var(--edge);
        border-left: 3px solid var(--cyan);
        color: var(--text) !important;
        font-family: 'Share Tech Mono', monospace;
        padding: 0.22rem 0.75rem;
        font-size: 0.8rem;
    }

    /* ---------- SECCIONES ---------- */
    .stApp .section-title {
        color: var(--cyan) !important;
        font-weight: 700;
        font-size: 1.15rem;
        letter-spacing: 0.05em;
        margin: 1.8rem 0 0.2rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid var(--edge);
        text-shadow: 0 0 10px var(--cyan-glow);
    }
    .stApp .section-sub {
        color: var(--text-dim) !important;
        font-size: 0.88rem;
        margin: 0.4rem 0 0.9rem 0;
    }

    /* ---------- ESTADO ---------- */
    .state {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        background: var(--panel);
        border: 1px solid var(--edge);
        clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 12px 100%, 0 calc(100% - 12px));
        padding: 0.8rem 1.2rem;
        margin-top: 0.9rem;
        font-weight: 500;
    }
    .stApp .state { color: var(--text) !important; }
    .dot { width: 10px; height: 10px; border-radius: 50%; background: #3A5368; flex-shrink: 0; }
    .state.on .dot { background: var(--cyan); box-shadow: 0 0 10px var(--cyan), 0 0 20px var(--cyan-glow); }
    .state.off .dot { background: var(--magenta); box-shadow: 0 0 10px var(--magenta), 0 0 20px var(--magenta-glow); }
    .state .tag {
        margin-left: auto;
        font-family: 'Share Tech Mono', monospace;
        padding: 0.12rem 0.9rem;
        font-size: 0.85rem;
        font-weight: 700;
        background: rgba(255,255,255,0.05);
        border: 1px solid var(--edge);
    }
    .stApp .state.on .tag { color: var(--cyan) !important; border-color: var(--cyan); background: rgba(0,229,255,0.1); }
    .stApp .state.off .tag { color: var(--magenta) !important; border-color: var(--magenta); background: rgba(255,46,136,0.1); }

    /* ---------- LECTURA DE VALOR ---------- */
    .valuecard {
        background: var(--panel);
        border: 1px solid var(--edge);
        clip-path: polygon(0 0, calc(100% - 18px) 0, 100% 18px, 100% 100%, 18px 100%, 0 calc(100% - 18px));
        padding: 1rem 1.4rem;
        margin: 0.5rem 0 0.9rem 0;
        display: flex;
        align-items: baseline;
        gap: 0.6rem;
    }
    .stApp .valuecard .label { color: var(--text-dim) !important; font-weight: 500; font-size: 0.9rem; }
    .stApp .valuecard .value {
        color: var(--cyan) !important;
        font-family: 'Share Tech Mono', monospace;
        font-size: 2.6rem;
        font-weight: 400;
        letter-spacing: 0.04em;
        margin-left: auto;
        text-shadow: 0 0 18px var(--cyan-glow);
    }

    /* ---------- BOTONES ---------- */
    .stButton > button {
        border: 1px solid var(--cyan);
        border-radius: 0;
        clip-path: polygon(0 0, calc(100% - 14px) 0, 100% 14px, 100% 100%, 14px 100%, 0 calc(100% - 14px));
        padding: 0.8rem 1rem;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 0.12em;
        background: rgba(0,229,255,0.1);
        box-shadow: 0 0 18px var(--cyan-glow), inset 0 0 14px rgba(0,229,255,0.15);
        transition: background 0.15s ease, box-shadow 0.15s ease;
    }
    .stButton > button, .stButton > button p, .stButton > button span { color: var(--cyan) !important; }
    .stButton > button:hover {
        background: var(--cyan);
        border: 1px solid var(--cyan);
        box-shadow: 0 0 26px var(--cyan);
    }
    .stButton > button:hover, .stButton > button:hover p, .stButton > button:hover span { color: var(--void) !important; }
    .stButton > button:focus-visible { outline: 2px solid var(--text); outline-offset: 2px; }

    .st-key-btn_off button {
        border-color: var(--magenta);
        background: rgba(255,46,136,0.1);
        box-shadow: 0 0 18px var(--magenta-glow), inset 0 0 14px rgba(255,46,136,0.15);
    }
    .st-key-btn_off button, .st-key-btn_off button p, .st-key-btn_off button span { color: var(--magenta) !important; }
    .st-key-btn_off button:hover { background: var(--magenta); border-color: var(--magenta); box-shadow: 0 0 26px var(--magenta); }
    .st-key-btn_off button:hover, .st-key-btn_off button:hover p, .st-key-btn_off button:hover span { color: var(--void) !important; }

    .st-key-btn_analog button { background: var(--panel-2); border-color: var(--edge); box-shadow: none; }
    .st-key-btn_analog button:hover { background: var(--cyan); border-color: var(--cyan); box-shadow: 0 0 26px var(--cyan); }

    /* ---------- SLIDER ---------- */
    [data-testid="stSlider"] [role="slider"] {
        background: var(--cyan) !important;
        box-shadow: 0 0 14px var(--cyan) !important;
        border: 2px solid var(--void) !important;
    }
    [data-testid="stSliderThumbValue"], [data-testid="stSliderThumbValue"] * {
        color: var(--cyan) !important;
        font-family: 'Share Tech Mono', monospace;
    }
    [data-testid="stTickBarMin"], [data-testid="stTickBarMax"] {
        color: var(--text-dim) !important;
        font-family: 'Share Tech Mono', monospace;
    }

    /* ---------- ALERTA ---------- */
    div[data-testid="stAlert"] {
        background: rgba(0,229,255,0.08) !important;
        border: 1px solid var(--cyan);
        border-radius: 0;
        box-shadow: 0 0 16px var(--cyan-glow);
    }
    div[data-testid="stAlert"] p { color: var(--cyan) !important; }

    #MainMenu, footer { visibility: hidden; }

    @media (prefers-reduced-motion: reduce) {
        .stButton > button { transition: none; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

values = 0.0
act1 = "OFF"


def on_publish(client, userdata, result):
    print("el dato ha sido publicado \n")
    pass


def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)


broker = "157.230.214.127"
port = 1883
client1 = paho.Client("samuel")
client1.on_message = on_message

if "last_act" not in st.session_state:
    st.session_state.last_act = None

st.markdown(
    f"""
    <div class="hero">
        <h1>🎛️ MQTT Control</h1>
        <p>Envía órdenes y valores analógicos a tu dispositivo por MQTT.</p>
        <div class="chips">
            <span class="chip">Broker: {broker}</span>
            <span class="chip">Puerto: {port}</span>
            <span class="chip">Python {platform.python_version()}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-title">💡 Actuador</div>'
    '<div class="section-sub">Enciende o apaga el actuador 1 (tópico: enviar1)</div>',
    unsafe_allow_html=True,
)

col_on, col_off = st.columns(2)

with col_on:
    if st.button("ON", key="btn_on", use_container_width=True):
        act1 = "ON"
        client1 = paho.Client("samuel")
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": act1})
        ret = client1.publish("enviar1", message)
        st.session_state.last_act = "ON"

with col_off:
    if st.button("OFF", key="btn_off", use_container_width=True):
        act1 = "OFF"
        client1 = paho.Client("samuel")
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": act1})
        ret = client1.publish("enviar1", message)
        st.session_state.last_act = "OFF"

last = st.session_state.last_act
if last:
    st.markdown(
        f"""
        <div class="state {last.lower()}">
            <span class="dot"></span>
            <span>Última orden enviada</span>
            <span class="tag">{last}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="state">
            <span class="dot"></span>
            <span>Aún no se ha enviado ninguna orden</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="section-title">🎚️ Valor analógico</div>'
    '<div class="section-sub">Elige un valor entre 0 y 100 y envíalo (tópico: enviar)</div>',
    unsafe_allow_html=True,
)

values = st.slider("Selecciona el rango de valores", 0.0, 100.0)

st.markdown(
    f"""
    <div class="valuecard">
        <span class="label">Valor seleccionado</span>
        <span class="value">{values:.1f}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.button("Enviar valor analógico", key="btn_analog", use_container_width=True):
    client1 = paho.Client("samuel")
    client1.on_publish = on_publish
    client1.connect(broker, port)
    message = json.dumps({"Analog": float(values)})
    ret = client1.publish("enviar", message)
    st.success(f"Valor {values:.1f} enviado correctamente", icon="✅")
    st.success(f"Valor {values:.1f} enviado correctamente", icon="✅")
 
