import os
import time

from trie import Trie
from indice_invertido import IndiceInvertido
from kmp import buscar_kmp
import preprocessamento as pp


class MotorBusca:
    def __init__(self, pasta_docs="documentos", arquivo_stopwords="stopwords.txt"):
        self.pasta_docs = pasta_docs
        self.arquivo_stopwords = arquivo_stopwords
        self._zerar()

    def _zerar(self):
        self.trie = Trie()
        self.indice = IndiceInvertido()
        self.textos = {}
        self.info_docs = {}
        self.total_palavras = 0
        self.vocabulario = set()
        self.tempo_preprocessamento = 0.0
        self.tempo_trie = 0.0
        self.tempo_indice = 0.0

    def construir(self):
        self._zerar()
        stopwords = pp.carregar_stopwords(self.arquivo_stopwords)

        t0 = time.perf_counter()
        tokens_por_doc = {}
        for nome in pp.listar_arquivos_txt(self.pasta_docs):
            texto = pp.ler_arquivo(os.path.join(self.pasta_docs, nome))
            tokens = pp.preprocessar(texto, stopwords)
            self.textos[nome] = texto
            tokens_por_doc[nome] = tokens
            self.total_palavras += len(tokens)
            self.vocabulario.update(tokens)
            self.info_docs[nome] = {
                "palavras": len(tokens),
                "distintas": len(set(tokens)),
                "caracteres": len(texto),
            }
        self.tempo_preprocessamento = time.perf_counter() - t0

        t0 = time.perf_counter()
        for termo in self.vocabulario:
            self.trie.inserir(termo)
        self.tempo_trie = time.perf_counter() - t0

        t0 = time.perf_counter()
        for nome, tokens in tokens_por_doc.items():
            self.indice.adicionar_documento(nome, tokens)
        self.tempo_indice = time.perf_counter() - t0

    def buscar_palavra(self, palavra):
        t0 = time.perf_counter()
        docs = self.indice.consultar(palavra.strip().lower())
        return docs, time.perf_counter() - t0

    def buscar_prefixo(self, prefixo, limite=None):
        t0 = time.perf_counter()
        palavras = self.trie.buscar_prefixo(prefixo.strip().lower(), limite)
        resultado = [(p, self.indice.consultar(p)) for p in palavras]
        return resultado, time.perf_counter() - t0

    def buscar_sequencia(self, sequencia):
        t0 = time.perf_counter()
        alvo = sequencia.lower()
        resultado = []
        if alvo:
            for nome, texto in self.textos.items():
                posicoes = buscar_kmp(texto.lower(), alvo)
                if posicoes:
                    p = posicoes[0]
                    ini, fim = max(0, p - 40), min(len(texto), p + len(alvo) + 40)
                    trecho = " ".join(texto[ini:fim].split())
                    resultado.append((nome, len(posicoes), trecho))
        return resultado, time.perf_counter() - t0

    def estatisticas(self):
        return {
            "Documentos processados": len(self.info_docs),
            "Total de palavras (após tokenização)": self.total_palavras,
            "Termos distintos (vocabulário)": len(self.vocabulario),
            "Palavras armazenadas na Trie": len(self.trie),
            "Nós da Trie": self.trie.total_nos,
            "Tempo de pré-processamento": formatar_tempo(self.tempo_preprocessamento),
            "Tempo de construção da Trie": formatar_tempo(self.tempo_trie),
            "Tempo de construção do índice invertido": formatar_tempo(self.tempo_indice),
        }


def formatar_tempo(segundos):
    if segundos < 1e-3:
        return f"{segundos * 1e6:.1f} µs"
    if segundos < 1:
        return f"{segundos * 1e3:.3f} ms"
    return f"{segundos:.3f} s"
