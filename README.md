# Python + APIs de IA — Semana 4

Conectando Python com Inteligência Artificial. Scripts que usam IA via API do Google Gemini.

---

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```
GEMINI_API_KEY=sua_chave_aqui
```

> O `.env` está no `.gitignore` e nunca será enviado ao GitHub.

Instale as dependências:

```bash
pip install google-genai python-dotenv
```

---

## Projetos

### Projeto 1 — Primeira Conversa com a API

Envia uma pergunta para o Gemini e exibe a resposta no terminal.

```bash
cd projeto1_primeira_conversa
python projeto1_primeira_conversa.py
```

---

### Projeto 2 — Assistente de Terminal

Assistente interativo no terminal com histórico de conversa.

```bash
python projeto2_Assistente_de_terminal.py
```

---

### Projeto 3 — Analisador de Texto com IA

Recebe texto e retorna JSON com resumo em 3 frases, sentimento e 5 palavras-chave.

```bash
cd "Projeto3_Analisador de Texto com IA"
python projeto3_analisador_de_texto.py
```

```
1 - Digitar texto manualmente
2 - Analisar arquivo .txt  →  salva resultado em analise.json
3 - Analisar pasta inteira de .txt  →  salva tudo em analise_completa.json
```

---

### Projeto 4 — Tradutor Inteligente com IA

Detecta o idioma e traduz para PT-BR de forma natural, adaptando expressões idiomáticas e culturais.

```bash
cd Projeto4_Tradutor_Inteligente
python projeto4_tradutor.py
```

```
1 - Digitar ou colar texto
2 - Traduzir arquivo .txt       →  salva resultado em <nome>_traduzido.json
3 - Traduzir pasta inteira .txt →  salva cada tradução em <nome>_pt.txt
```

---

## Modelo utilizado

`gemini-2.5-flash` via Google Generative AI
