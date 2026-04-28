import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def analisar(texto):
    prompt = f"""Analise o texto abaixo e retorne SOMENTE um JSON válido com esta estrutura exata (sem markdown, sem explicações):

{{
  "resumo": ["frase 1", "frase 2", "frase 3"],
  "sentimento": "bom | pessimo | normal",
  "palavras_chave": ["palavra1", "palavra2", "palavra3", "palavra4", "palavra5"]
}}

Regras:
- "resumo": exatamente 3 frases resumindo o texto
- "sentimento": escolha apenas UMA das três opções — "bom", "pessimo" ou "normal"
- "palavras_chave": crie exatamente 5 palavras ou expressões mais relevantes do texto

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


def analisar_arquivo(caminho_txt):
    caminho = Path(caminho_txt)
    texto = caminho.read_text(encoding="utf-8")
    resultado = analisar(texto)

    saida = caminho.with_name("analise.json")
    saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✔ Arquivo analisado: {caminho.name}")
    print(f"  Resultado salvo em: {saida.name}")
    return resultado


def analisar_pasta(caminho_pasta):
    pasta = Path(caminho_pasta)
    arquivos = list(pasta.glob("*.txt"))

    if not arquivos:
        print("Nenhum arquivo .txt encontrado na pasta.")
        return

    print(f"\nEncontrados {len(arquivos)} arquivo(s) .txt\n")
    todos = {}

    for i, arquivo in enumerate(arquivos):
        texto = arquivo.read_text(encoding="utf-8")
        resultado = analisar(texto)
        todos[arquivo.name] = resultado
        print(f"✔ {arquivo.name} → sentimento: {resultado['sentimento']}")
        if i < len(arquivos) - 1:
            time.sleep(3)

    saida = pasta / "analise_completa.json"
    saida.write_text(json.dumps(todos, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nTodos os resultados salvos em: {saida}")


# ─── Menu principal ────────────────────────────────────────────────────────────

print("=== Analisador de Texto com IA ===")
print("1 - Digitar texto manualmente")
print("2 - Analisar arquivo .txt")
print("3 - Analisar pasta inteira de .txt")
opcao = input("\nEscolha uma opção: ").strip()

if opcao == "1":
    texto = input("\nCole o texto:\n> ")
    resultado = analisar(texto)
    print("\n=== Resultado ===")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))

elif opcao == "2":
    caminho = input("\nCaminho do arquivo .txt: ").strip()
    resultado = analisar_arquivo(caminho)
    print("\n=== Resultado ===")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))

elif opcao == "3":
    pasta = input("\nCaminho da pasta: ").strip()
    analisar_pasta(pasta)

else:
    print("Opção inválida.")
