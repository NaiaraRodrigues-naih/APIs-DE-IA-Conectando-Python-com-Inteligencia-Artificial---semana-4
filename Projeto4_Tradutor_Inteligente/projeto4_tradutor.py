import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def traduzir(texto):
    prompt = f"""Você é um tradutor especialista. Analise o texto abaixo e retorne SOMENTE um JSON válido (sem markdown, sem explicações):

{{
  "idioma_detectado": "nome do idioma em português",
  "codigo_idioma": "código ISO ex: en, es, fr, de, ja, zh",
  "traducao": "tradução completa e natural para o Português Brasileiro",
  "nota_tradutor": "observação opcional sobre expressões, gírias ou contexto cultural — deixe vazio se não houver"
}}

Regras:
- Traduza de forma natural e fluente, não literal — preserve o tom, humor e intenção do original
- Adapte expressões idiomáticas para equivalentes em PT-BR quando existirem
- Se o texto já estiver em PT-BR, informe isso e retorne o texto original em "traducao"

Texto:
{texto}"""

    for tentativa in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            break
        except Exception as e:
            if tentativa < 2:
                print(f"  API indisponível, tentando novamente em 10s... ({tentativa + 1}/3)")
                time.sleep(10)
            else:
                raise e

    raw = response.text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw.strip())


def traduzir_arquivo(caminho_txt):
    caminho = Path(caminho_txt)
    texto = caminho.read_text(encoding="utf-8")
    resultado = traduzir(texto)

    saida = caminho.with_stem(caminho.stem + "_traduzido").with_suffix(".json")
    saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✔ Arquivo traduzido: {caminho.name}")
    print(f"  Idioma detectado: {resultado['idioma_detectado']} ({resultado['codigo_idioma']})")
    print(f"  Resultado salvo em: {saida.name}")
    return resultado


def traduzir_pasta(caminho_pasta):
    pasta = Path(caminho_pasta)
    arquivos = [f for f in pasta.glob("*.txt") if not f.stem.endswith("_pt")]

    if not arquivos:
        print("Nenhum arquivo .txt encontrado na pasta.")
        return

    print(f"\nEncontrados {len(arquivos)} arquivo(s) .txt\n")

    for i, arquivo in enumerate(arquivos):
        texto = arquivo.read_text(encoding="utf-8")
        resultado = traduzir(texto)

        saida_txt = arquivo.with_stem(arquivo.stem + "_pt")
        saida_txt.write_text(resultado["traducao"], encoding="utf-8")

        print(f"✔ {arquivo.name} → {resultado['idioma_detectado']} ({resultado['codigo_idioma']}) → {saida_txt.name}")

        if i < len(arquivos) - 1:
            time.sleep(3)

    print(f"\nConcluído. {len(arquivos)} arquivo(s) traduzido(s) na pasta: {pasta}")


def exibir_resultado(resultado):
    print("\n" + "=" * 50)
    print(f"  Idioma detectado : {resultado['idioma_detectado']} ({resultado['codigo_idioma']})")
    print("=" * 50)
    print(f"\n{resultado['traducao']}")
    if resultado.get("nota_tradutor"):
        print(f"\n  Nota do tradutor: {resultado['nota_tradutor']}")
    print()


# ─── Menu principal ────────────────────────────────────────────────────────────

print("=== Tradutor Inteligente com IA ===")
print("Detecta o idioma e traduz para Português Brasileiro\n")
print("1 - Digitar ou colar texto")
print("2 - Traduzir arquivo .txt")
print("3 - Traduzir pasta inteira de .txt  →  salva com _pt no nome")
opcao = input("\nEscolha uma opção: ").strip()

if opcao == "1":
    print("\nCole o texto (Enter duas vezes para finalizar):")
    linhas = []
    try:
        while True:
            linha = input()
            if linha == "" and linhas and linhas[-1] == "":
                break
            linhas.append(linha)
    except EOFError:
        pass
    texto = "\n".join(linhas).strip()

    if not texto:
        print("Nenhum texto informado.")
    else:
        print("\nTraduzindo...")
        resultado = traduzir(texto)
        exibir_resultado(resultado)

elif opcao == "2":
    caminho = input("\nCaminho do arquivo .txt: ").strip()
    print("\nTraduzindo...")
    resultado = traduzir_arquivo(caminho)
    exibir_resultado(resultado)

elif opcao == "3":
    pasta = input("\nCaminho da pasta: ").strip()
    traduzir_pasta(pasta)

else:
    print("Opção inválida.")
