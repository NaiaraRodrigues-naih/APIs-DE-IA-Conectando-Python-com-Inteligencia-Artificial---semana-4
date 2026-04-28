import os
import time
from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # sem janela — salva direto em arquivo
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PALETA = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3", "#937860"]


# ─── Análise com Pandas ────────────────────────────────────────────────────────

def analisar_csv(caminho: str) -> tuple[pd.DataFrame, dict]:
    df = pd.read_csv(caminho)

    analise = {
        "arquivo": Path(caminho).name,
        "linhas": len(df),
        "colunas": list(df.columns),
        "tipos": df.dtypes.astype(str).to_dict(),
        "nulos": df.isnull().sum().to_dict(),
        "estatisticas": df.describe(include="all").to_string(),
    }

    colunas_num = df.select_dtypes(include="number").columns.tolist()
    if colunas_num:
        analise["correlacoes"] = df[colunas_num].corr().round(3).to_string()

    # Agregações inteligentes por coluna categórica
    agregacoes = {}
    for col in df.select_dtypes(include="object").columns:
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
        f"\nTipos de dados:\n" + "\n".join(f"  {k}: {v}" for k, v in analise["tipos"].items()),
        f"\nValores nulos:\n" + "\n".join(f"  {k}: {v}" for k, v in analise["nulos"].items()),
        f"\nEstatísticas descritivas:\n{analise['estatisticas']}",
    ]

    if "correlacoes" in analise:
        linhas.append(f"\nCorrelações:\n{analise['correlacoes']}")

    if "agregacoes_por_categoria" in analise:
        linhas.append("\nAgregações por categoria:")
        for cat, tabela in analise["agregacoes_por_categoria"].items():
            linhas.append(f"\n  Por {cat}:\n{tabela}")

    return "\n".join(linhas)


# ─── Geração de gráficos com Matplotlib ───────────────────────────────────────

_COLUNAS_TEMPO = {"mes", "mês", "month", "data", "date", "ano", "year", "periodo", "período", "semana", "week", "trimestre", "quarter"}


def _eh_coluna_tempo(nome: str) -> bool:
    return nome.lower() in _COLUNAS_TEMPO


def _formatar_eixo_brl(ax, eixo="y"):
    def fmt(x, _):
        if x >= 1_000_000:
            return f"R$ {x/1_000_000:.1f}M"
        if x >= 1_000:
            return f"R$ {x/1_000:.0f}k"
        return f"R$ {x:.0f}"
    locator = mticker.FuncFormatter(fmt)
    if eixo == "y":
        ax.yaxis.set_major_formatter(locator)
    else:
        ax.xaxis.set_major_formatter(locator)


def gerar_graficos(df: pd.DataFrame, pasta_saida: Path) -> list[tuple[str, str]]:
    """Gera gráficos relevantes e retorna lista de (caminho_relativo, descricao)."""
    pasta_saida.mkdir(parents=True, exist_ok=True)
    graficos = []

    cols_num = df.select_dtypes(include="number").columns.tolist()
    cols_cat = [c for c in df.select_dtypes(include="object").columns if df[c].nunique() <= 20]
    col_tempo = next((c for c in df.columns if _eh_coluna_tempo(c)), None)

    if not cols_num:
        return graficos

    col_principal = cols_num[0]  # primeira coluna numérica como métrica principal

    # 1. Gráfico de linha — evolução temporal
    if col_tempo and col_tempo in df.columns:
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

    # 2. Barras — soma da métrica principal por categoria
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

    # 3. Pizza — distribuição de uma segunda categoria (se existir)
    if len(cats_sem_tempo) >= 2:
        col_cat2 = cats_sem_tempo[1]
        dados_pizza = df.groupby(col_cat2)[col_principal].sum()
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(
            dados_pizza.values,
            labels=dados_pizza.index,
            autopct="%1.1f%%",
            colors=PALETA[:len(dados_pizza)],
            startangle=140,
        )
        ax.set_title(f"Participação por {col_cat2}", fontsize=13, fontweight="bold")
        fig.tight_layout()
        caminho = pasta_saida / f"pizza_{col_cat2}.png"
        fig.savefig(caminho, dpi=120)
        plt.close(fig)
        graficos.append((caminho.name, f"Distribuição percentual de {col_principal} por {col_cat2}"))

    # 4. Barras empilhadas — categoria × tempo (se ambos disponíveis)
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
    """Gera a seção Markdown com as imagens referenciadas."""
    if not graficos:
        return ""
    linhas = ["\n\n## Gráficos\n"]
    for nome, descricao in graficos:
        caminho_rel = f"{pasta_graficos}/{nome}"
        linhas.append(f"### {descricao}\n\n![{descricao}]({caminho_rel})\n")
    return "\n".join(linhas)


# ─── Geração do relatório via IA ───────────────────────────────────────────────

def gerar_relatorio(dados_str: str, foco: str = "", graficos: list[tuple[str, str]] | None = None) -> str:
    instrucao_foco = f"\nFoco especial solicitado pelo analista: {foco}" if foco else ""

    if graficos:
        lista_graficos = "\n".join(f"- {desc} (arquivo: {nome})" for nome, desc in graficos)
        instrucao_graficos = f"""
Os seguintes gráficos foram gerados automaticamente a partir dos dados e serão inseridos no relatório:
{lista_graficos}

Ao longo do relatório, mencione esses gráficos nas seções mais relevantes usando frases como:
"Conforme ilustrado no gráfico de evolução temporal..." ou "Como pode ser visto no gráfico de barras...".
NÃO insira os links Markdown das imagens — eles serão adicionados automaticamente após o texto."""
    else:
        instrucao_graficos = ""

    prompt = f"""Você é um analista de dados sênior. Com base nos dados abaixo, produza um relatório executivo completo em Markdown.

O relatório deve conter obrigatoriamente:
1. **Sumário Executivo** — 3-4 frases resumindo os achados mais importantes
2. **Principais Métricas** — tabela ou lista com os KPIs mais relevantes
3. **Análise por Segmento** — insights por categoria, região ou período (conforme os dados)
4. **Tendências Identificadas** — padrões, sazonalidade, crescimento ou queda
5. **Pontos de Atenção** — riscos, anomalias ou oportunidades que merecem ação
6. **Recomendações** — 3-5 ações concretas baseadas nos dados
7. **Próximos Passos** — o que investigar ou monitorar a seguir
{instrucao_graficos}{instrucao_foco}

Use linguagem executiva, objetiva e orientada a resultados. Inclua números e percentuais sempre que possível.

---
DADOS ANALISADOS:
{dados_str}
---"""

    for tentativa in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            if tentativa < 2:
                print(f"  API indisponível, tentando novamente em 10s... ({tentativa + 1}/3)")
                time.sleep(10)
            else:
                raise e



# ─── Salvar relatório ──────────────────────────────────────────────────────────

def salvar_relatorio(relatorio: str, nome_base: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"relatorio_{nome_base}_{timestamp}.md"
    caminho_saida = Path(nome_arquivo)
    caminho_saida.write_text(relatorio, encoding="utf-8")
    return caminho_saida


# ─── Menu principal ────────────────────────────────────────────────────────────

print("=" * 55)
print("   Projeto 5 — Relatório Executivo com Dados + IA")
print("=" * 55)
print("\nEste script carrega um CSV, analisa com Pandas e usa")
print("a API Gemini para gerar um relatório executivo em Markdown.\n")

caminho_csv = input("Caminho do arquivo CSV (Enter para usar o exemplo): ").strip()
if not caminho_csv:
    caminho_csv = "vendas_exemplo.csv"

caminho_csv = Path(caminho_csv)
if not caminho_csv.exists():
    print(f"\nArquivo não encontrado: {caminho_csv}")
    exit(1)

print(f"\nCarregando: {caminho_csv.name}...")
df, analise = analisar_csv(str(caminho_csv))

print(f"✔ {analise['linhas']} linhas carregadas — colunas: {', '.join(analise['colunas'])}")

foco = input("\nAlgum foco específico para o relatório? (Enter para pular): ").strip()

# Gráficos
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
nome_pasta_graficos = f"graficos_{caminho_csv.stem}_{timestamp}"
pasta_graficos = Path(nome_pasta_graficos)

print("\nGerando gráficos...")
graficos = gerar_graficos(df, pasta_graficos)
for _, desc in graficos:
    print(f"  ✔ {desc}")

if not graficos:
    print("  (nenhum gráfico gerado — dados sem colunas numéricas suficientes)")

# Relatório via IA
print("\nGerando relatório com IA...")
dados_str = formatar_analise(analise)
relatorio = gerar_relatorio(dados_str, foco, graficos)

# Injeta seção de gráficos ao final do relatório Markdown
secao_graficos = bloco_graficos_md(graficos, nome_pasta_graficos)
relatorio_final = relatorio + secao_graficos

caminho_saida = salvar_relatorio(relatorio_final, caminho_csv.stem)

print(f"\n✔ Relatório salvo em: {caminho_saida}")
if graficos:
    print(f"✔ Gráficos salvos em: {pasta_graficos}/")
print("\n" + "=" * 55)
print("PRÉVIA DO RELATÓRIO")
print("=" * 55)
print(relatorio_final[:1500])
if len(relatorio_final) > 1500:
    print(f"\n... ({len(relatorio_final) - 1500} caracteres restantes no arquivo)")
