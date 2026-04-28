# Projeto 4 — Tradutor Inteligente com IA

Detecta o idioma automaticamente e traduz para Português Brasileiro de forma natural. Adapta expressões idiomáticas e culturais — não traduz palavra por palavra.

## Instalação

```bash
pip install google-genai python-dotenv
```

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```
GEMINI_API_KEY=sua_chave_aqui
```

## Como usar

```bash
python projeto4_tradutor.py
```

```
1 - Digitar ou colar texto
2 - Traduzir arquivo .txt  →  salva resultado em <nome>_traduzido.json
```

## Exemplo de saída

```json
{
  "idioma_detectado": "Inglês",
  "codigo_idioma": "en",
  "traducao": "Está caindo o mundo lá fora...",
  "nota_tradutor": "'raining cats and dogs' adaptado para 'está caindo o mundo'"
}
```

## Idiomas testados

| Arquivo | Idioma | Expressão adaptada |
|---|---|---|
| `teste_en.txt` | Inglês | *raining cats and dogs* → "está caindo o mundo" |
| `teste_es.txt` | Espanhol | *levantarse con el pie derecho* → "acordar com o pé direito" |
| `teste_fr.txt` | Francês | *tomber dans les pommes* → "apaguei" |
| `teste_zh.txt` | Mandarim | *屋漏偏逢连夜雨* → "uma desgraça nunca vem sozinha" |

## Modelo utilizado

`gemini-2.5-flash` via Google Generative AI
