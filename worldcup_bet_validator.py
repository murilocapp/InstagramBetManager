"""
================================================================================
worldcup_bet_validator.py
================================================================================
Descrição : Coleta comentários de posts do Instagram via Instaloader,
            extrai e valida apostas de resultados da Copa do Mundo,
            e gera leaderboard de acertos por usuário.

Uso       : python worldcup_bet_validator.py \
                --input input.csv \
                --output-dir ./output \
                --username SEU_USUARIO

Dependências : instaloader, pandas, unidecode
================================================================================
"""

import argparse
import getpass
import logging
import re
import sys
from pathlib import Path

import instaloader
import pandas as pd
import unidecode

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Ingestão
# ──────────────────────────────────────────────

def get_comments(post_shortcode: str, loader: instaloader.Instaloader) -> pd.DataFrame:
    """
    Extrai comentários de um post do Instagram via shortcode.

    Parameters
    ----------
    post_shortcode : str
        Código identificador do post (ex: 'CxYz123ABC').
    loader : instaloader.Instaloader
        Instância autenticada do Instaloader.

    Returns
    -------
    pd.DataFrame
        Colunas: username, comment, comment_date, shortcode, post_date.
    """
    post = instaloader.Post.from_shortcode(loader.context, post_shortcode)
    rows = [
        {
            "username":     c.owner.username,
            "comment":      c.text,
            "comment_date": c.created_at_utc,
            "shortcode":    post_shortcode,
            "post_date":    post.date,
        }
        for c in post.get_comments()
    ]
    return pd.DataFrame(rows)


def collect_all_comments(
    input_data: pd.DataFrame,
    loader: instaloader.Instaloader,
    output_dir: Path,
) -> pd.DataFrame:
    """
    Itera sobre todos os dias e shortcodes do CSV de entrada,
    coletando comentários. Salva progresso parcial em caso de erro.

    Parameters
    ----------
    input_data : pd.DataFrame
        DataFrame com colunas 'Day' e 'shortcode'.
    loader : instaloader.Instaloader
        Instância autenticada do Instaloader.
    output_dir : Path
        Diretório onde o arquivo de progresso será salvo.

    Returns
    -------
    pd.DataFrame
        Todos os comentários coletados concatenados.
    """
    chunks: list[pd.DataFrame] = []

    try:
        for day in input_data["Day"].unique():
            shortcodes = input_data.loc[input_data["Day"] == day, "shortcode"]
            log.info(f"Coletando dia {day} — {len(shortcodes)} post(s)")
            for shortcode in shortcodes:
                chunks.append(get_comments(shortcode, loader))

    except Exception as e:
        log.error(f"Erro durante coleta: {e}")
        if chunks:
            progress_path = output_dir / "progress.csv"
            pd.concat(chunks, ignore_index=True).to_csv(progress_path, index=False)
            log.warning(f"Progresso parcial salvo em: {progress_path}")
        raise

    return pd.concat(chunks, ignore_index=True)


# ──────────────────────────────────────────────
# Transformação
# ──────────────────────────────────────────────

def extract_bet(comment: str) -> str | None:
    """
    Extrai padrão de aposta (ex: '2x1 Brasil') de um comentário bruto.

    Parameters
    ----------
    comment : str
        Texto do comentário.

    Returns
    -------
    str | None
        String normalizada da aposta ou None se não encontrado.
    """
    pattern = r"(\d+\s*x\s*\d+)\s*(\w+)"
    match = re.search(pattern, comment)
    if match:
        return f"{match.group(1).replace(' ', '')} {match.group(2)}"
    return None


def normalize_string(s: str) -> str:
    """Remove acentos e converte para lowercase."""
    if isinstance(s, str):
        return unidecode.unidecode(s).lower()
    return s


def split_numbers_text(s: str) -> tuple[str, str]:
    """
    Separa dígitos e texto de uma string normalizada.

    Returns
    -------
    tuple[str, str]
        (numeros_concatenados, texto_normalizado)
    """
    if not isinstance(s, str):
        return "", ""
    numbers = "".join(re.findall(r"\d+", s))
    text = normalize_string(re.sub(r"\d+", "", s).strip())
    return numbers, text


def _normalize_for_comparison(s: str) -> str:
    """Reduz string a formato canônico para comparação de apostas."""
    numbers, text = split_numbers_text(s)
    return f"{numbers} {text}".strip()


def validate_bet(
    row: pd.Series,
    bet_column: str = "bet",
    result_column: str = "result",
    comment_column: str = "comment",
) -> bool:
    """
    Valida se a aposta bate com o resultado esperado.
    Usa 'bet' quando disponível; fallback para 'comment' bruto.

    Parameters
    ----------
    row : pd.Series
        Linha do DataFrame com colunas de aposta, resultado e comentário.
    bet_column : str
        Nome da coluna com a aposta extraída.
    result_column : str
        Nome da coluna com o resultado esperado.
    comment_column : str
        Nome da coluna com o comentário bruto (fallback).

    Returns
    -------
    bool
        True se aposta == resultado após normalização.
    """
    candidate = row[bet_column] if row[bet_column] is not None else row[comment_column]
    return _normalize_for_comparison(candidate) == _normalize_for_comparison(row[result_column])


def transform(data: pd.DataFrame, input_data: pd.DataFrame) -> pd.DataFrame:
    """
    Junta comentários com metadados, extrai e valida apostas.

    Parameters
    ----------
    data : pd.DataFrame
        Comentários coletados do Instagram.
    input_data : pd.DataFrame
        CSV de entrada com shortcodes e resultados esperados.

    Returns
    -------
    pd.DataFrame
        DataFrame enriquecido com colunas 'bet' e 'bet_result'.
    """
    df = data.merge(input_data, on="shortcode", how="left")
    df["bet"] = df["comment"].apply(extract_bet)
    df["bet_result"] = df.apply(validate_bet, axis=1)
    df.drop_duplicates(inplace=True)
    return df


def build_leaderboard(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega acertos por usuário e ordena por pontuação.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame com colunas 'username' e 'bet_result'.

    Returns
    -------
    pd.DataFrame
        Leaderboard com colunas 'username' e 'score'.
    """
    leaderboard = (
        df.groupby("username")["bet_result"]
        .apply(lambda x: x.sum())
        .reset_index(name="score")
        .sort_values("score", ascending=False)
        .reset_index(drop=True)
    )
    return leaderboard


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Valida apostas de Copa do Mundo a partir de comentários do Instagram."
    )
    parser.add_argument(
        "--input", type=Path, required=True,
        help="Caminho para o CSV de entrada (colunas: Day, shortcode, result)."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("."),
        help="Diretório para salvar os arquivos de saída (default: diretório atual)."
    )
    parser.add_argument(
        "--username", type=str, required=True,
        help="Usuário do Instagram para autenticação."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    password = getpass.getpass(f"Senha do Instagram para '{args.username}': ")

    log.info("Autenticando no Instagram...")
    loader = instaloader.Instaloader()
    loader.login(args.username, password)

    log.info(f"Lendo input: {args.input}")
    input_data = pd.read_csv(args.input)

    log.info("Iniciando coleta de comentários...")
    data = collect_all_comments(input_data, loader, args.output_dir)

    raw_path = args.output_dir / "data_all_days.csv"
    data.to_csv(raw_path, index=False)
    log.info(f"Dados brutos salvos em: {raw_path}")

    log.info("Transformando e validando apostas...")
    df = transform(data, input_data)

    data_path = args.output_dir / "data.csv"
    df.to_csv(data_path, index=False)
    log.info(f"Dados processados salvos em: {data_path}")

    leaderboard = build_leaderboard(df)

    lb_path = args.output_dir / "leaderboard.csv"
    leaderboard.to_csv(lb_path, index=False)
    log.info(f"Leaderboard salvo em: {lb_path}")

    print("\n── Top 10 ──────────────────────")
    print(leaderboard.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
