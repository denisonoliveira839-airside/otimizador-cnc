import streamlit as st
import matplotlib.pyplot as plt
import random

st.set_page_config(layout="wide")

st.title("🔥 Otimizador CNC Fancoil - Nível Industrial")

# -------------------------------
# ENTRADA
# -------------------------------
col1, col2 = st.columns(2)

with col1:
    largura_chapa = st.number_input("Largura da chapa (mm)", value=2000)
    altura_chapa = st.number_input("Altura da chapa (mm)", value=1000)

with col2:
    diametro_fresa = st.number_input("Diâmetro da fresa (mm)", value=6)
    espacamento = st.number_input("Espaçamento (mm)", value=5)

permitir_rotacao = st.checkbox("Permitir rotação")

qtd = st.number_input("Quantidade de peças", 1, 50, 5)

pecas = []

for i in range(qtd):
    with st.expander(f"Peça {i+1}"):
        l = st.number_input(f"Largura {i}", key=f"l{i}")
        a = st.number_input(f"Altura {i}", key=f"a{i}")
        pecas.append({"id": i+1, "l": l, "a": a})

# -------------------------------
# BOTÃO
# -------------------------------
if st.button("🚀 Gerar Layout"):

    # Ordenação
    pecas.sort(key=lambda x: max(x["l"], x["a"]), reverse=True)

    x = 0
    y = 0
    linha_altura = 0

    resultado = []
    nao_couberam = []

    # -------------------------------
    # NESTING
    # -------------------------------
    for p in pecas:
        l, a = p["l"], p["a"]

        opcoes = [(l, a)]
        if permitir_rotacao:
            opcoes.append((a, l))

        colocado = False

        for (w, h) in opcoes:
            if x + w + espacamento <= largura_chapa:
                resultado.append({
                    "id": p["id"],
                    "x": x,
                    "y": y,
                    "w": w,
                    "h": h
                })
                x += w + espacamento
                linha_altura = max(linha_altura, h + espacamento)
                colocado = True
                break

        if not colocado:
            x = 0
            y += linha_altura
            linha_altura = 0

            for (w, h) in opcoes:
                if y + h + espacamento <= altura_chapa:
                    resultado.append({
                        "id": p["id"],
                        "x": x,
                        "y": y,
                        "w": w,
                        "h": h
                    })
                    x += w + espacamento
                    linha_altura = max(linha_altura, h + espacamento)
                    colocado = True
                    break

        if not colocado:
            nao_couberam.append(p)

    # -------------------------------
    # RESULTADO TEXTO
    # -------------------------------
    st.subheader("📐 Layout")

    for r in resultado:
        st.write(f"Peça {r['id']} → X:{r['x']} Y:{r['y']} | {r['w']} x {r['h']} mm")

    if nao_couberam:
        st.error("Peças que não couberam:")
        for p in nao_couberam:
            st.write(f"Peça {p['id']} ({p['l']} x {p['a']})")

    # -------------------------------
    # APROVEITAMENTO
    # -------------------------------
    area_total = largura_chapa * altura_chapa
    area_usada = sum(r["w"] * r["h"] for r in resultado)

    st.success(f"Aproveitamento: {(area_usada/area_total)*100:.2f}%")

    # -------------------------------
    # DESENHO (CAD)
    # -------------------------------
    st.subheader("🧱 Visual da Chapa")

    fig, ax = plt.subplots(figsize=(10, 5))

    # chapa
    ax.add_patch(plt.Rectangle((0, 0), largura_chapa, altura_chapa, fill=False, linewidth=2))

    for r in resultado:
        cor = (random.random(), random.random(), random.random())

        rect = plt.Rectangle(
            (r["x"], r["y"]),
            r["w"],
            r["h"],
            facecolor=cor,
            edgecolor='black'
        )

        ax.add_patch(rect)

        # texto
        ax.text(
            r["x"] + r["w"]/2,
            r["y"] + r["h"]/2,
            f"P{r['id']}\n{r['w']}x{r['h']}",
            ha='center',
            va='center',
            fontsize=8,
            color='black'
        )

    ax.set_xlim(0, largura_chapa)
    ax.set_ylim(0, altura_chapa)
    ax.set_aspect('equal')

    plt.gca().invert_yaxis()

    st.pyplot(fig)

    # -------------------------------
    # GCODE
    # -------------------------------
    if st.button("⚙️ Gerar G-code"):

        gcode = []
        offset = diametro_fresa / 2

        gcode.append("G21")
        gcode.append("G90")
        gcode.append("G0 Z5")

        for r in resultado:
            x = r["x"] + offset
            y = r["y"] + offset
            w = r["w"] - diametro_fresa
            h = r["h"] - diametro_fresa

            gcode.append(f"; Peça {r['id']}")
            gcode.append(f"G0 X{x} Y{y}")
            gcode.append("G1 Z-2 F300")
            gcode.append(f"G1 X{x+w} Y{y}")
            gcode.append(f"G1 X{x+w} Y{y+h}")
            gcode.append(f"G1 X{x} Y{y+h}")
            gcode.append(f"G1 X{x} Y{y}")
            gcode.append("G0 Z5")

        gcode.append("G0 X0 Y0")
        gcode.append("M30")

        st.code("\n".join(gcode))
