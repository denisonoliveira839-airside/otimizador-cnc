# =========================================
# OTIMIZADOR CNC FANCOIL - VERSÃO PROFISSIONAL
# =========================================

def coletar_dados():
    print("=== OTIMIZADOR CNC FANCOIL ===")

    largura_chapa = float(input("Largura da chapa (mm): "))
    altura_chapa = float(input("Altura da chapa (mm): "))

    diametro_fresa = float(input("Diâmetro da fresa (mm): "))
    espacamento = float(input("Espaçamento mínimo entre peças (mm): "))

    permitir_rotacao = input("Permitir rotação das peças? (s/n): ").lower() == "s"

    pecas = []
    qtd = int(input("Quantidade de peças: "))

    for i in range(qtd):
        print(f"\nPeça {i+1}")
        l = float(input("Largura: "))
        a = float(input("Altura: "))
        pecas.append({"id": i+1, "l": l, "a": a})

    return largura_chapa, altura_chapa, diametro_fresa, espacamento, permitir_rotacao, pecas


def nesting(largura_chapa, altura_chapa, espacamento, permitir_rotacao, pecas):
    # Ordena peças maiores primeiro
    pecas.sort(key=lambda x: max(x["l"], x["a"]), reverse=True)

    x = 0
    y = 0
    linha_altura = 0

    resultado = []
    nao_couberam = []

    for p in pecas:
        l = p["l"]
        a = p["a"]

        opcoes = [(l, a)]
        if permitir_rotacao:
            opcoes.append((a, l))

        colocado = False

        for (w, h) in opcoes:
            largura_real = w + espacamento
            altura_real = h + espacamento

            if x + largura_real <= largura_chapa:
                resultado.append({
                    "id": p["id"],
                    "x": x,
                    "y": y,
                    "w": w,
                    "h": h
                })

                x += largura_real
                linha_altura = max(linha_altura, altura_real)
                colocado = True
                break

        if not colocado:
            # nova linha
            x = 0
            y += linha_altura
            linha_altura = 0

            for (w, h) in opcoes:
                largura_real = w + espacamento
                altura_real = h + espacamento

                if y + altura_real <= altura_chapa:
                    resultado.append({
                        "id": p["id"],
                        "x": x,
                        "y": y,
                        "w": w,
                        "h": h
                    })

                    x += largura_real
                    linha_altura = max(linha_altura, altura_real)
                    colocado = True
                    break

        if not colocado:
            nao_couberam.append(p)

    return resultado, nao_couberam


def calcular_aproveitamento(largura_chapa, altura_chapa, resultado):
    area_total = largura_chapa * altura_chapa
    area_usada = sum(r["w"] * r["h"] for r in resultado)
    return (area_usada / area_total) * 100


def gerar_gcode(resultado, diametro_fresa, profundidade=-2):
    print("\n=== GCODE GERADO ===")

    offset = diametro_fresa / 2

    print("G21 ; mm")
    print("G90 ; absoluto")
    print("G0 Z5")

    for r in resultado:
        x = r["x"] + offset
        y = r["y"] + offset
        w = r["w"] - diametro_fresa
        h = r["h"] - diametro_fresa

        print(f"\n; Peça {r['id']}")

        # aproximação segura
        print(f"G0 X{x-5} Y{y-5}")
        print("G0 Z5")

        # entrada suave
        print(f"G1 X{x} Y{y} F800")
        print(f"G1 Z{profundidade} F300")

        # corte
        print(f"G1 X{x+w} Y{y}")
        print(f"G1 X{x+w} Y{y+h}")
        print(f"G1 X{x} Y{y+h}")
        print(f"G1 X{x} Y{y}")

        # saída
        print("G0 Z5")

    print("\nG0 X0 Y0")
    print("M30")


def mostrar_resultado(resultado, nao_couberam, aproveitamento):
    print("\n=== LAYOUT FINAL ===")

    for r in resultado:
        print(f"Peça {r['id']} -> X:{r['x']:.1f} Y:{r['y']:.1f} | {r['w']} x {r['h']} mm")

    if nao_couberam:
        print("\n--- NÃO COUBERAM ---")
        for p in nao_couberam:
            print(f"Peça {p['id']} ({p['l']} x {p['a']})")

    print(f"\nAproveitamento: {aproveitamento:.2f}%")


def main():
    dados = coletar_dados()

    resultado, nao_couberam = nesting(
        dados[0], dados[1], dados[3], dados[4], dados[5]
    )

    aproveitamento = calcular_aproveitamento(
        dados[0], dados[1], resultado
    )

    mostrar_resultado(resultado, nao_couberam, aproveitamento)

    gerar = input("\nGerar G-code? (s/n): ").lower() == "s"
    if gerar:
        gerar_gcode(resultado, dados[2])


if __name__ == "__main__":
    main()
