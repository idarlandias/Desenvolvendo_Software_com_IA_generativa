"""Download e verificacao do corpus de PDFs para LAB-002/003/004.

Uso:
    python datasets/download.py [--out data/corpus] [--verify]

- Baixa 3 papers do arXiv para `data/corpus/`
- Calcula SHA256 e grava em `datasets/SHA256SUMS`
- Em re-execucoes, verifica SHA256 contra `SHA256SUMS` existente e aborta se divergir
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import sys
from pathlib import Path
from urllib.request import Request, urlopen

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("corpus-download")

CORPUS: list[dict[str, str]] = [
    {
        "filename": "attention-is-all-you-need.pdf",
        "url": "https://arxiv.org/pdf/1706.03762v7.pdf",
        "arxiv_id": "1706.03762",
        "title": "Attention Is All You Need (Vaswani et al, 2017)",
    },
    {
        "filename": "rag-knowledge-intensive-nlp.pdf",
        "url": "https://arxiv.org/pdf/2005.11401v4.pdf",
        "arxiv_id": "2005.11401",
        "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP (Lewis 2020)",
    },
    {
        "filename": "lost-in-the-middle.pdf",
        "url": "https://arxiv.org/pdf/2307.03172v3.pdf",
        "arxiv_id": "2307.03172",
        "title": "Lost in the Middle: How Language Models Use Long Contexts (Liu et al, 2023)",
    },
]

USER_AGENT = "aulas-ppi-corpus-fetcher/1.0 (https://github.com/sidi/aulas-ppi)"

MAX_SIZE_MB = 25  # cada paper deve ficar bem abaixo disso; defesa contra redirect inesperado


def sha256_of(path: Path) -> str:
    """Calcula SHA256 de um arquivo em chunks (eficiente em arquivos grandes)."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download_one(entry: dict[str, str], out_dir: Path) -> Path:
    """Baixa um PDF, validando tamanho e tipo de conteudo."""
    dest = out_dir / entry["filename"]
    if dest.exists():
        log.info("ja existe: %s (%.1f MB)", dest.name, dest.stat().st_size / 1e6)
        return dest

    log.info("baixando: %s -> %s", entry["url"], dest.name)
    req = Request(entry["url"], headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=60) as resp:
        content_type = resp.headers.get("Content-Type", "")
        if "application/pdf" not in content_type:
            raise RuntimeError(
                f"{entry['filename']}: Content-Type inesperado '{content_type}' "
                f"(esperado application/pdf)"
            )
        data = resp.read()

    size_mb = len(data) / 1e6
    if size_mb > MAX_SIZE_MB:
        raise RuntimeError(f"{entry['filename']}: {size_mb:.1f} MB > limite {MAX_SIZE_MB} MB")

    dest.write_bytes(data)
    log.info("  ok: %.1f MB", size_mb)
    return dest


def load_existing_sums(sums_path: Path) -> dict[str, str]:
    """Le SHA256SUMS existente (formato: '<hash>  <filename>')."""
    if not sums_path.exists():
        return {}
    out: dict[str, str] = {}
    for line in sums_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        out[parts[1].strip()] = parts[0].strip()
    return out


def write_sums(sums_path: Path, sums: dict[str, str]) -> None:
    """Grava SHA256SUMS em formato canonico."""
    lines = ["# SHA256SUMS — corpus de papers para software-com-ia-generativa", ""]
    for name in sorted(sums):
        lines.append(f"{sums[name]}  {name}")
    sums_path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        default="data/corpus",
        help="diretorio de saida (default: data/corpus)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="apenas verificar SHA256; nao baixar arquivos ausentes",
    )
    args = parser.parse_args()

    out_dir = Path(args.out)
    sums_path = Path(__file__).parent / "SHA256SUMS"

    if not args.verify:
        out_dir.mkdir(parents=True, exist_ok=True)
        for entry in CORPUS:
            download_one(entry, out_dir)

    existing = load_existing_sums(sums_path)
    current: dict[str, str] = {}
    failures: list[str] = []

    for entry in CORPUS:
        dest = out_dir / entry["filename"]
        if not dest.exists():
            log.warning("ausente: %s", dest)
            continue
        actual = sha256_of(dest)
        current[entry["filename"]] = actual
        expected = existing.get(entry["filename"])
        if expected and expected != actual:
            failures.append(
                f"{entry['filename']}: SHA256 divergente\n"
                f"  esperado: {expected}\n  obtido:   {actual}"
            )
        elif not expected:
            log.info("novo: %s = %s", entry["filename"], actual)

    if failures:
        for f in failures:
            log.error(f)
        return 1

    if not existing:
        write_sums(sums_path, current)
        log.info("SHA256SUMS gravado em %s", sums_path)
    else:
        log.info("SHA256SUMS verificado contra %d arquivos", len(current))

    return 0


if __name__ == "__main__":
    sys.exit(main())
