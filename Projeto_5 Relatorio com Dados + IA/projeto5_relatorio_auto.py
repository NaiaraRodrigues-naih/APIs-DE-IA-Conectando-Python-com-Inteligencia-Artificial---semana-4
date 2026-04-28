"""
Versão automática do Projeto 5 — sem input(), ideal para agendamento.

Uso:
    python projeto5_relatorio_auto.py
    python projeto5_relatorio_auto.py --csv meus_dados.csv
    python projeto5_relatorio_auto.py --csv meus_dados.csv --foco "desempenho regional"
"""
import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from dotenv import load_dotenv
from google import genai

# ─── Carrega .env — busca na pasta do script e na pasta pai (raiz do projeto) ──
_dir = Path(__file__).parent
load_dotenv(_dir / ".env") or load_dotenv(_dir.parent / ".env")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERRO: GEMINI_API_KEY não encontrada no .env")
    sys.exit(1)

client = genai.Client(api_key=api_key)

PALETA = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3", "#937860"]

# ─── Argumentos de linha de comando ───────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(description="Gera relatório executivo a partir de CSV usando IA")
    parser.add_argument(
        "--csv",
        default="vendas_exemplo.csv",
        help="Caminho do arquivo CSV (padrão: vendas_exemplo.csv)",
    )
    parser.add_argument(
        "--foco",
        default="",
        help="Foco específico para o relatório (opcional)",
    )
    return parser.parse_args()


# ─── Análise com Pandas ────────────────────────────────────────────────────────

def analisar_csv(caminho: str) -> tuple[pd.DataFrame, dict]:
    df = pd.read_csv(caminho)
    colunas_num = df.select_dtypes(include="number").columns.tolist()

    analise = {
        "arquivo": Path(caminho).name,
        "linhas": len(df),
        "colunas": list(df.columns),
        "tipos": df.dtypes.astype(str).to_dict(),
        "nulos": df.isnull().sum().to_dict(),
        "estatisticas": df.describe(include="all").to_string(),
    }

    if colunas_num:
        analise["correlacoes"] = df[colunas_num].corr().round(3).to_string()

    agregacoes = {}
    for col in df.select_dtypes(include=["object", "string"]).columns:
        if df[col].nunique() <= 20:
            grupo = df.groupby(col)[colunas_num].sum() if colunas_num else None
            if grupo is not None:
                agregacoes[col] = grupo.to_string()
    if agregacoes:
        analise["agregacoes_por_categoria"] = agregacoes

    return df, analise


def formatar_analise(analise: dict) -> str:
    linhas = [
        f"Arquivo: {analise['arquivo']}",
        f"Dimensões: {analise['linhas']} linhas × {len(analise['colunas'])} colunas",
        f"Colunas: {', '.join(analise['colunas'])}",
        "\nTipos de dados:\n" + "\n".join(f"  {k}: {v}" for k, v in analise["tipos"].items()),
        "\nValores nulos:\n" + "\n".join(f"  {k}: {v}" for k, v in analise["nulos"].items()),
        f"\nEstatísticas descritivas:\n{analise['estatisticas']}",
    ]
    if "correlacoes" in analise:
        linhas.append(f"\nCorrelações:\n{analise['correlacoes']}")
    if "agregacoes_por_categoria" in analise:
        linhas.append("\nAgregações por categoria:")
        for cat, tabela in analise["agregacoes_por_categoria"].items():
            linhas.append(f"\n  Por {cat}:\n{tabela}")
    return "\n".join(linhas)


# ─── Gráficos ─────────────────────────────────────────────────────────────────

_COLUNAS_TEMPO = {"mes", "mês", "month", "data", "date", "ano", "year", "periodo", "período", "semana", "week", "trimestre", "quarter"}


def _eh_coluna_tempo(nome: str) -> bool:
    return nome.lower() in _COLUNAS_TEMPO


def gerar_graficos(df: pd.DataFrame, pasta_saida: Path) -> list[tuple[str, str]]:
    pasta_saida.mkdir(parents=True, exist_ok=True)
    graficos = []

    cols_num = df.select_dtypes(include="number").columns.tolist()
    cols_cat = [c for c in df.select_dtypes(include=["object", "string"]).columns if df[c].nunique() <= 20]
    col_tempo = next((c for c in df.columns if _eh_coluna_tempo(c)), None)

    if not cols_num:
        return graficos

    col_principal = cols_num[0]

    if col_tempo:
        fig, ax = plt.subplots(figsize=(9, 4))
        dados_tempo = df.groupby(col_tempo)[cols_num].sum()
        for i, col in enumerate(cols_num[:3]):
            ax.plot(dados_tempo.index, dados_tempo[col], marker="o", label=col, color=PALETA[i % len(PALETA)])
        ax.set_title(f"Evolução por {col_tempo}", fontsize=13, fontweight="bold")
        ax.set_xlabel(col_tempo)
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        fig.tight_layout()
        caminho = pasta_saida / "evolucao_temporal.png"
        fig.savefig(caminho, dpi=120)
        plt.close(fig)
        graficos.append((caminho.name, f"Evolução de {', '.join(cols_num[:3])} ao longo do tempo ({col_tempo})"))

    cats_sem_tempo = [c for c in cols_cat if not _eh_coluna_tempo(c)]

    if cats_sem_tempo:
        col_cat = cats_sem_tempo[0]
        dados_bar = df.groupby(col_cat)[col_principal].sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(8, 4))
        barras = ax.bar(dados_bar.index, dados_bar.values, color=PALETA[:len(dados_bar)])
        ax.set_title(f"{col_principal} por {col_cat}", fontsize=13, fontweight="bold")
        ax.set_xlabel(col_cat)
        ax.bar_label(barras, fmt=lambda v: f"{v:,.0f}", padding=3, fontsize=8)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        plt.xticks(rotation=30, ha="right")
        fig.tight_layout()
        caminho = pasta_saida / f"barras_{col_cat}.png"
        fig.savefig(caminho, dpi=120)
        plt.close(fig)
        graficos.append((caminho.name, f"Total de {col_principal} agrupado por {col_cat}"))

    if len(cats_sem_tempo) >= 2:
        col_cat2 = cats_sem_tempo[1]
        dados_pizza = df.groupby(col_cat2)[col_principal].sum()
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(dados_pizza.values, labels=dados_pizza.index, autopct="%1.1f%%",
               colors=PALETA[:len(dados_pizza)], startangle=140)
        ax.set_title(f"Participação por {col_cat2}", fontsize=13, fontweight="bold")
        fig.tight_layout()
        caminho = pasta_saida / f"pizza_{col_cat2}.png"
        fig.savefig(caminho, dpi=120)
        plt.close(fig)
        graficos.append((caminho.name, f"Distribuição percentual de {col_principal} por {col_cat2}"))

    if col_tempo and cats_sem_tempo:
        col_cat = cats_sem_tempo[0]
        try:
            pivot = df.pivot_table(index=col_tempo, columns=col_cat, values=col_principal, aggfunc="sum", fill_value=0)
            fig, ax = plt.subplots(figsize=(9, 4))
            pivot.plot(kind="bar", stacked=True, ax=ax, color=PALETA[:len(pivot.columns)])
            ax.set_title(f"{col_principal} por {col_tempo} e {col_cat}", fontsize=13, fontweight="bold")
            ax.set_xlabel(col_tempo)
            ax.legend(title=col_cat, bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
            plt.xticks(rotation=30, ha="right")
            ax.grid(axis="y", linestyle="--", alpha=0.5)
            fig.tight_layout()
            caminho = pasta_saida / f"empilhado_{col_tempo}_{col_cat}.png"
            fig.savefig(caminho, dpi=120)
            plt.close(fig)
            graficos.append((caminho.name, f"{col_principal} empilhado por {col_cat} ao longo do {col_tempo}"))
        except Exception:
            pass

    return graficos


def bloco_graficos_md(graficos: list[tuple[str, str]], pasta_graficos: str) -> str:
    if not graficos:
        return ""
    linhas = ["\n\n## Gráficos\n"]
    for nome, descricao in graficos:
        linhas.append(f"### {descricao}\n\n![{descricao}]({pasta_graficos}/{nome})\n")
    return "\n".join(linhas)


# ─── Relatório via IA ──────────────────────────────────────────────────────────

def gerar_relatorio(dados_str: str, foco: str = "", graficos: list[tuple[str, str]] | None = None) -> str:
    instrucao_foco = f"\nFoco especial: {foco}" if foco else ""

    if graficos:
        lista = "\n".join(f"- {desc} (arquivo: {nome})" for nome, desc in graficos)
        instrucao_graficos = f"""
Gráficos gerados automaticamente (mencione-os nas seções relevantes, NÃO insira os links Markdown):
{lista}"""
    else:
        instrucao_graficos = ""

    prompt = f"""Você é um analista de dados sênior. Produza um relatório executivo completo em Markdown com:
1. **Sumário Executivo** — 3-4 frases com os achados principais
2. **Principais Métricas** — tabela com KPIs
3. **Análise por Segmento** — insights por categoria, região ou período
4. **Tendências Identificadas** — padrões, sazonalidade, crescimento ou queda
5. **Pontos de Atenção** — riscos, anomalias ou oportunidades
6. **Recomendações** — 3-5 ações concretas
7. **Próximos Passos** — o que monitorar a seguir
{instrucao_graficos}{instrucao_foco}

Use linguagem executiva e inclua números e percentuais sempre que possível.

---
DADOS:
{dados_str}
---"""

    for tentativa in range(3):
        try:
            response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            return response.text.strip()
        except Exception as e:
            if tentativa < 2:
                print(f"  API indisponível, tentando novamente em 10s... ({tentativa + 1}/3)")
                time.sleep(10)
            else:
                raise e


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    caminho_csv = Path(__file__).parent / args.csv
    if not caminho_csv.exists():
        print(f"ERRO: arquivo não encontrado: {caminho_csv}")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")

    print(f"[{data_hoje}] Carregando {caminho_csv.name}...")
    df, analise = analisar_csv(str(caminho_csv))
    print(f"  {analise['linhas']} linhas | colunas: {', '.join(analise['colunas'])}")

    nome_pasta = f"graficos_{caminho_csv.stem}_{timestamp}"
    pasta_graficos = Path(__file__).parent / nome_pasta

    print("  Gerando gráficos...")
    graficos = gerar_graficos(df, pasta_graficos)
    for _, desc in graficos:
        print(f"    ✔ {desc}")

    print("  Gerando relatório com IA...")
    dados_str = formatar_analise(analise)
    relatorio = gerar_relatorio(dados_str, args.foco, graficos)

    secao_graficos = bloco_graficos_md(graficos, nome_pasta)
    relatorio_final = relatorio + secao_graficos

    nome_arquivo = f"relatorio_{caminho_csv.stem}_{timestamp}.md"
    caminho_saida = Path(__file__).parent / nome_arquivo
    caminho_saida.write_text(relatorio_final, encoding="utf-8")

    print(f"  ✔ Relatório salvo: {nome_arquivo}")
    if graficos:
        print(f"  ✔ Gráficos em: {nome_pasta}/")
    print(f"[{data_hoje}] Concluído.")


if __name__ == "__main__":
    main()
