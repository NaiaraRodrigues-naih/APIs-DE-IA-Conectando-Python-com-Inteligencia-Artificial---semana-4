from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

VERDE = "\033[92m"
BRANCO = "\033[97m"
CINZA = "\033[90m"
RESET = "\033[0m"

SYSTEM_PROMPT = """Você é um assistente especializado em cibersegurança.
Ajuda com: análise de vulnerabilidades, boas práticas de segurança, CTFs,
redes, criptografia, pentest ético e defesa de sistemas.
Responda de forma clara, técnica e responsável.
Nunca forneça instruções para atividades ilegais ou prejudiciais."""

historico = []


def chat(mensagem_usuario):
    historico.append({"role": "user", "content": mensagem_usuario})

    resposta = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=historico,
    )

    conteudo = resposta.content[0].text
    historico.append({"role": "assistant", "content": conteudo})

    uso = resposta.usage
    return conteudo, uso.input_tokens, uso.output_tokens


def main():
    print("=" * 60)
    print("  Assistente de Cibersegurança - Kensei")
    print("  Digite 'sair' ou 'exit' para encerrar")
    print("  Digite 'limpar' para resetar o histórico")
    print("=" * 60)
    print()

    while True:
        try:
            entrada = input(f"{BRANCO}Você: {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando...")
            break

        if not entrada:
            continue

        if entrada.lower() in ("sair", "exit", "quit"):
            print("Até logo!")
            break

        if entrada.lower() == "limpar":
            historico.clear()
            print(f"{CINZA}[Histórico resetado]{RESET}\n")
            continue

        resposta, tokens_entrada, tokens_saida = chat(entrada)
        print(f"\n{VERDE}Assistente: {resposta}{RESET}")
        print(f"{CINZA}[tokens: {tokens_entrada} entrada / {tokens_saida} saída]{RESET}\n")


if __name__ == "__main__":
    main()
