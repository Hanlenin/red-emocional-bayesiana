import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import json
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Red Emocional Bayesiana Personal", layout="wide")

# Mensaje de bienvenida
st.title("🧠 Red Emocional Bayesiana Personal")
st.markdown("### Trazando el mapa de mi mundo interno, un evento a la vez.")
st.write("---")

# Input de nombre y fecha
nombre_usuario = st.text_input("Ingresa tu nombre:", value="Hans")
fecha_actual = datetime.today().strftime('%Y-%m-%d')

# Mensaje personalizado
st.success(f"👋 Hola {nombre_usuario}, hoy es {fecha_actual}. ¡Un buen día para conocerte mejor!")

# Inicializar sesión
if "network_data" not in st.session_state:
    st.session_state.network_data = []

# Sidebar para agregar eventos
st.sidebar.header("➕ Agregar evento emocional")
evento = st.sidebar.text_input("Nombre del evento", value="Crítica")
int_1 = st.sidebar.text_input("Interpretación 1", value="Me ayudan")
int_2 = st.sidebar.text_input("Interpretación 2", value="Me humillan")
int_3 = st.sidebar.text_input("Interpretación 3", value="Reflexiono")

prior_1 = st.sidebar.number_input("P1 (creencia previa)", 0.0, 1.0, 0.2)
prior_2 = st.sidebar.number_input("P2 (creencia previa)", 0.0, 1.0, 0.6)
prior_3 = st.sidebar.number_input("P3 (creencia previa)", 0.0, 1.0, 0.2)

lik_1 = st.sidebar.slider("P(Estímulo | Int 1)", 0.0, 1.0, 0.1)
lik_2 = st.sidebar.slider("P(Estímulo | Int 2)", 0.0, 1.0, 0.8)
lik_3 = st.sidebar.slider("P(Estímulo | Int 3)", 0.0, 1.0, 0.3)

if st.sidebar.button("Agregar evento"):
    ev = lik_1 * prior_1 + lik_2 * prior_2 + lik_3 * prior_3
    post_1 = (lik_1 * prior_1) / ev if ev != 0 else 0
    post_2 = (lik_2 * prior_2) / ev if ev != 0 else 0
    post_3 = (lik_3 * prior_3) / ev if ev != 0 else 0

    caso = {
        "fecha": fecha_actual,
        "nombre": nombre_usuario,
        "evento": evento,
        "interpretaciones": [
            {"respuesta": int_1, "posterior": round(post_1 * 100, 1)},
            {"respuesta": int_2, "posterior": round(post_2 * 100, 1)},
            {"respuesta": int_3, "posterior": round(post_3 * 100, 1)},
        ]
    }
    st.session_state.network_data.append(caso)

st.write("---")
st.subheader("🧩 Mi Red Emocional del Día")

if st.session_state.network_data:
    # Mostrar resumen
    data = []
    for caso in st.session_state.network_data:
        for interp in caso["interpretaciones"]:
            data.append([
                caso["fecha"], caso["nombre"], caso["evento"],
                interp["respuesta"], f'{interp["posterior"]}%'
            ])
    df = pd.DataFrame(data, columns=["Fecha", "Nombre", "Evento", "Interpretación", "Posterior"])
    st.dataframe(df, use_container_width=True)

    # Grafo emocional
    G = nx.DiGraph()
    pos = {}
    x = 0
    for item in st.session_state.network_data:
        evt = f'{item["evento"]} ({item["fecha"]})'
        G.add_node(evt)
        pos[evt] = (x, 3)
        for j, interp in enumerate(item["interpretaciones"]):
            nodo = f'{interp["respuesta"]} ({interp["posterior"]}%)'
            G.add_node(nodo)
            G.add_edge(evt, nodo)
            pos[nodo] = (x - 1 + j, 2)
        x += 3

    fig, ax = plt.subplots(figsize=(14, 6))
    nx.draw(
        G, pos, with_labels=True, node_color="lightblue",
        node_size=3000, font_size=9, font_weight="bold", edge_color="gray", ax=ax
    )
    st.pyplot(fig)

    # Descargar JSON
    st.download_button(
        label="📄 Descargar diario emocional (JSON)",
        data=json.dumps(st.session_state.network_data, indent=4),
        file_name=f"diario_emocional_{fecha_actual}.json",
        mime="application/json"
    )

    # Descargar imagen PNG
    fig.savefig(f"grafo_emocional_{fecha_actual}.png")
    with open(f"grafo_emocional_{fecha_actual}.png", "rb") as file:
        btn = st.download_button(
            label="🖼️ Descargar red emocional (PNG)",
            data=file,
            file_name=f"grafo_emocional_{fecha_actual}.png",
            mime="image/png"
        )

    st.info("✨ Reconociendo mis emociones, reescribiendo mi historia.")
else:
    st.warning("Aún no has registrado eventos emocionales hoy. ¡Anímate a comenzar!")


