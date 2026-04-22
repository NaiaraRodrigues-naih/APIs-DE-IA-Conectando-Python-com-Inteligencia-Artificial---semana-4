# Projeto 2: Assistente de Terminal

Chatbot de terminal especializado em cibersegurança, com histórico de conversa e interface colorida, usando a API da Anthropic (Claude).

## Funcionalidades

- Conversa contínua com histórico completo (multi-turn)
- System prompt com personalidade de especialista em cibersegurança
- Cores no terminal: IA em verde, usuário em branco
- Exibe tokens consumidos por resposta
- Comandos `limpar` e `sair` integrados

## Tecnologias

- Python 3.10+
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) — modelo `claude-sonnet-4-6`
- `python-dotenv` — gerenciamento de variáveis de ambiente

## Instalação

```bash
pip install anthropic python-dotenv
```

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```
ANTHROPIC_API_KEY=sua_chave_aqui
```

## Execução

```bash
python projeto2_Assistente_de_terminal.py
```

## Comandos disponíveis

| Comando | Ação |
|---|---|
| `limpar` | Reseta o histórico da conversa |
| `sair` / `exit` | Encerra o programa |

## Segurança

O arquivo `.env` está listado no `.gitignore` — a API Key nunca é enviada ao repositório.
