class NoTrie:
    __slots__ = ("filhos", "fim_palavra")

    def __init__(self):
        self.filhos = {}
        self.fim_palavra = False


class Trie:
    def __init__(self):
        self.raiz = NoTrie()
        self.total_palavras = 0
        self.total_nos = 1

    def inserir(self, palavra):
        if not palavra:
            return False
        no = self.raiz
        for caractere in palavra:
            proximo = no.filhos.get(caractere)
            if proximo is None:
                proximo = NoTrie()
                no.filhos[caractere] = proximo
                self.total_nos += 1
            no = proximo
        if no.fim_palavra:
            return False
        no.fim_palavra = True
        self.total_palavras += 1
        return True

    def _localizar(self, texto):
        no = self.raiz
        for caractere in texto:
            no = no.filhos.get(caractere)
            if no is None:
                return None
        return no

    def buscar(self, palavra):
        if not palavra:
            return False
        no = self._localizar(palavra)
        return no is not None and no.fim_palavra

    def buscar_prefixo(self, prefixo, limite=None):
        no = self._localizar(prefixo)
        if no is None:
            return []
        resultado = []
        pilha = [(no, prefixo)]
        while pilha:
            atual, texto = pilha.pop()
            if atual.fim_palavra:
                resultado.append(texto)
                if limite is not None and len(resultado) >= limite:
                    break
            for c in sorted(atual.filhos, reverse=True):
                pilha.append((atual.filhos[c], texto + c))
        return resultado

    def __len__(self):
        return self.total_palavras

    def __contains__(self, palavra):
        return self.buscar(palavra)
