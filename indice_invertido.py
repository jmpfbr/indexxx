class IndiceInvertido:
    def __init__(self):
        self.indice = {}

    def adicionar_documento(self, nome_doc, tokens):
        for termo in tokens:
            docs = self.indice.get(termo)
            if docs is None:
                docs = set()
                self.indice[termo] = docs
            docs.add(nome_doc)

    def consultar(self, termo):
        return sorted(self.indice.get(termo, ()))

    def __len__(self):
        return len(self.indice)
