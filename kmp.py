def tabela_lps(padrao):
    lps = [0] * len(padrao)
    k = 0
    for i in range(1, len(padrao)):
        while k > 0 and padrao[i] != padrao[k]:
            k = lps[k - 1]
        if padrao[i] == padrao[k]:
            k += 1
        lps[i] = k
    return lps


def buscar_kmp(texto, padrao):
    if not padrao:
        return []
    lps = tabela_lps(padrao)
    posicoes = []
    j = 0
    for i, c in enumerate(texto):
        while j > 0 and c != padrao[j]:
            j = lps[j - 1]
        if c == padrao[j]:
            j += 1
        if j == len(padrao):
            posicoes.append(i - j + 1)
            j = lps[j - 1]
    return posicoes
