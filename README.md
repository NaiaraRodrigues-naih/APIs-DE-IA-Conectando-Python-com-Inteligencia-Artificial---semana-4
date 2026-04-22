# Assistente de Terminal - Cibersegurança

Chatbot de terminal com histórico de conversa, especializado em cibersegurança, usando a API da Anthropic (Claude).

## Funcionalidades

- Loop contínuo: você digita, a IA responde
- Histórico completo da conversa (multi-turn)
- System prompt focado em cibersegurança
- Cores no terminal: respostas da IA em verde, prompt do usuário em branco
- Exibe tokens consumidos a cada resposta

## Conceitos aplicados

| Conceito | Função |
|---|---|
| `role: system` | Define a personalidade e especialização da IA |
| `role: user` | Mensagem enviada pelo usuário |
| `role: assistant` | Resposta gerada pela IA |
| `historico` | Lista que mantém toda a conversa e é reenviada a cada chamada |
| `while True` | Loop contínuo que mantém o terminal ativo |
| `.append()` | Adiciona cada mensagem ao histórico |

## Pré-requisitos

- Python 3.10+
- Conta na [Anthropic](https://console.anthropic.com) com API Key

## Instalação

```bash
pip install anthropic python-dotenv
```

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```
ANTHROPIC_API_KEY=sua_chave_aqui
```

> O arquivo `.env` já está no `.gitignore` — sua chave nunca será enviada ao GitHub.

## Como usar

```bash
python projeto2_Assistente_de_terminal.py
```

### Comandos disponíveis

| Comando | Ação |
|---|---|
| `limpar` | Reseta o histórico da conversa |
| `sair` / `exit` | Encerra o programa |

## Exemplo

```
============================================================
  Assistente de Cibersegurança - Kensei
  Digite 'sair' ou 'exit' para encerrar
  Digite 'limpar' para resetar o histórico
============================================================

Você: o que é SQL Injection?

Assistente: SQL Injection é uma vulnerabilidade...
[tokens: 312 entrada / 94 saída]
```

## Tecnologias

- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- Modelo: `claude-sonnet-4-6`
- `python-dotenv` para gerenciamento de variáveis de ambiente
