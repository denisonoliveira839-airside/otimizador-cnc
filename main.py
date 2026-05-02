import streamlit as st

st.title("🔥 Otimizador CNC Fancoil")

# -------------------------------
# ENTRADA
# -------------------------------
largura_chapa = st.number_input("Largura da chapa (mm)", value=2000)
altura_chapa = st.number_input("Altura da chapa (mm)", value=1000)

diametro_fresa = st.number_input("Diâmetro da fresa (mm)", value=6)
espacamento = st.number_input("Espaçamento entre peças (mm)", value=5)

permitir_rotacao = st.checkbox("Permitir rotação")

qtd = st.number_input("Quantidade de peças", 1, 50, 3)

pecas = []

for i in range(qtd):
    st.subheader(f"Peça {i+1}")
    l = st.number_input(f"Largura {i}", key=f"l{i}")
    a = st.number_input(f"Altura {i}", key=f"a{i}")
    pecas.append({"id": i+1, "l": l, "a": a})

# -------------------------------
# PROCESSAMENTO
# -------------------------------
if st.button("Gerar Layout"):

    pecas.sort(key=lambda x: max(x["l"], x["a"]), reverse=True)

    x = 0
    y = 0
    linha_altura = 0

    resultado = []

    for p in pecas:
        l = p["l"]
        a = p["a"]

        opcoes = [(l, a)]
        if permitir_rotacao:
            opcoes.append((a, l))

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
                break
        else:
            x = 0
            y += linha_altura
            linha_altura = 0

    # -------------------------------
    # SAÍDA
    # -------------------------------
    st.subheader("📐 Layout")

    for r in resultado:
        st.write(f"Peça {r['id']} → X:{r['x']} Y:{r['y']} | {r['w']} x {r['h']} mm")

    # Aproveitamento
    area_total = largura_chapa * altura_chapa
    area_usada = sum(r["w"] * r["h"] for r in resultado)

    st.success(f"Aproveitamento: {(area_usada/area_total)*100:.2f}%")

    # -------------------------------
    # GCODE
    # -------------------------------
    if st.button("Gerar G-code"):

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
