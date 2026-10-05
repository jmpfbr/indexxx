import os
import re

_REGEX_TOKEN = re.compile(r"[^\W\d_]+", re.UNICODE)


def ler_arquivo(caminho):
    for codificacao in ("utf-8-sig", "latin-1"):
        try:
            with open(caminho, "r", encoding=codificacao) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return ""


def listar_arquivos_txt(pasta):
    if not os.path.isdir(pasta):
        return []
    return sorted(
        nome for nome in os.listdir(pasta)
        if nome.lower().endswith(".txt") and os.path.isfile(os.path.join(pasta, nome))
    )


def carregar_stopwords(caminho):
    if not os.path.isfile(caminho):
        return set()
    stop = set()
    for linha in ler_arquivo(caminho).splitlines():
        linha = linha.strip().lower()
        if linha and not linha.startswith("#"):
            stop.add(linha)
    return stop


def tokenizar(texto):
    return _REGEX_TOKEN.findall(texto.lower())


def preprocessar(texto, stopwords):
    return [t for t in tokenizar(texto) if t not in stopwords]
