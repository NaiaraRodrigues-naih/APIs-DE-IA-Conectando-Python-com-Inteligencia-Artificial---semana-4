# Projeto 3 — Analisador de Texto com IA

Script que recebe texto e pede para a IA resumir em 3 frases, identificar o sentimento e extrair 5 palavras-chave. Retorna JSON.

## Instalação

```bash
pip install google-genai python-dotenv
```

## Configuração

Crie um arquivo `.env` na raiz do repositório:

```
GEMINI_API_KEY=sua_chave_aqui
```

> O arquivo `.env` está no `.gitignore` e nunca será enviado ao GitHub.

## Como usar

```bash
python projeto3_analisador_de_texto.py
```

Escolha uma das opções:

```
1 - Digitar texto manualmente
2 - Analisar arquivo .txt  (salva resultado em analise.json)
3 - Analisar pasta inteira de .txt  (salva tudo em analise_completa.json)
```

## Exemplo de saída

```json
{
  "resumo": [
    "frase 1",
    "frase 2",
    "frase 3"
  ],
  "sentimento": "bom",
  "palavras_chave": [
    "palavra1",
    "palavra2",
    "palavra3",
    "palavra4",
    "palavra5"
  ]
}
```

## Modelo utilizado

`gemini-2.5-flash` via Google Generative AI
