# Projeto 1 — Primeira Conversa com a API

Script Python que envia uma pergunta digitada pelo usuário para a API do Google Gemini e imprime a resposta no terminal.

## O que faz

- Solicita ao usuário que digite uma pergunta no terminal
- Envia a pergunta para o modelo `gemini-2.5-flash` via API do Google Gemini
- Imprime a pergunta e a resposta no terminal

## Tecnologias

- Python 3
- [google-genai](https://pypi.org/project/google-genai/) — SDK oficial do Google Gemini
- [python-dotenv](https://pypi.org/project/python-dotenv/) — carrega variáveis de ambiente do arquivo `.env`

## Como usar

1. Instale as dependências:
   ```bash
   pip install google-genai python-dotenv
   ```

2. Crie um arquivo `.env` na raiz do projeto com sua chave da API:
   ```
   GEMINI_API_KEY=sua_chave_aqui
   ```
   > Gere sua chave gratuitamente em [aistudio.google.com](https://aistudio.google.com)

3. Execute o script:
   ```bash
   python projeto1_primeira_conversa.py
   ```

4. Digite sua pergunta quando solicitado.

## Segurança

A chave da API fica armazenada no arquivo `.env`, que está listado no `.gitignore` e **nunca é enviado ao GitHub**.
