# Relatório Técnico — Processamento e Busca de Textos

**Disciplina:** Análise e Otimização de Sistemas — Prof. André Lucio
**Trabalho Prático A1 — Unidade 2** · **Integrantes:** João Marcos Fierro, Geovanna Melo, Danielle Carvalho

## 1. Descrição da solução
O projeto tem duas partes que compartilham a mesma Trie. A **Parte I** é um autocomplete sobre uma lista de palavras (`palavras.txt`). A **Parte II** é um mini mecanismo de busca que lê todos os `.txt` de uma pasta, pré-processa, monta o vocabulário, insere-o na Trie, constrói um índice invertido sobre Hash e responde consultas por palavra, por prefixo e (bônus) por sequência de caracteres via KMP. Há interface gráfica (Tkinter) e versões em terminal.

Módulos: `trie.py`, `preprocessamento.py`, `indice_invertido.py`, `kmp.py`, `motor_busca.py` (integração e cronometragem), `gui.py`, `cli.py`, `autocomplete.py`, `main.py`.

## 2. A Trie e suas operações
Cada `NoTrie` tem um dicionário `filhos` (caractere → nó) e a flag `fim_palavra`. Palavras com prefixo comum **compartilham o mesmo caminho** a partir da raiz: `computador` e `computação` dividem os nós de `c-o-m-p-u-t-a` e só se separam depois.

- `inserir(palavra)`: percorre/cria um nó por caractere e marca o último como fim de palavra.
- `buscar(palavra)`: desce pelos caracteres; existe se chegar a um nó com `fim_palavra = True`.
- `buscar_prefixo(prefixo)`: desce até o nó do prefixo e faz um percurso em profundidade (iterativo) coletando as palavras descendentes, em ordem alfabética.

## 3. Autocomplete e busca por prefixo
Ao digitar `comp`, a Trie leva ao nó do prefixo em O(m) e devolve todas as palavras abaixo dele. Na Parte II, cada palavra devolvida pela Trie é consultada no índice invertido (Hash) para informar seus documentos: **Trie → termos; Hash → documentos**.

## 4. Pré-processamento
1. Conversão para minúsculas. 2. Remoção de pontuação e números. 3. Tokenização, feita com a expressão regular `[^\W\d_]+` (sequências de letras, incluindo acentuadas; todo o resto vira separador). 4. Remoção de stopwords (`stopwords.txt`, editável).
Exemplo: `"Os Algoritmos de Busca são muito importantes."` → `algoritmos | busca | importantes`. Stemming/lematização **não** foi implementado.

## 5. Vocabulário e índice invertido
O vocabulário é o conjunto (`set`) de termos distintos de todos os documentos, inserido integralmente na Trie. O índice invertido tem o formato `palavra → {arquivos}`.
**Por que "invertido"?** O mapeamento natural é documento → palavras que ele contém. O índice faz o sentido inverso: palavra → documentos. Assim, responder "onde aparece X?" não exige ler os arquivos, apenas uma consulta na tabela.

## 6. Uso de Hash
O índice é um `dict` do Python, ou seja, uma **tabela hash**. Uma *função hash* transforma a chave (a palavra) num número inteiro, que determina a posição do valor na tabela; por isso a busca não depende da quantidade de termos. A complexidade **média é O(1)** para inserir e consultar. Quando duas chaves distintas caem na mesma posição ocorre uma **colisão**; o Python a resolve com endereçamento aberto (sondagem), e no pior caso (muitas colisões) a operação degrada para O(n), o que é raro com boas funções hash. Os conjuntos de documentos (`set`) também são tabelas hash, evitando duplicatas em O(1) médio.

## 7. Complexidade das principais operações
Notação: m = tamanho da palavra/prefixo; n = total de tokens; V = termos distintos; D = documentos; N = nós da subárvore do prefixo; k = palavras devolvidas.

| Operação | Complexidade |
|---|---|
| Inserir na Trie | O(m) |
| Busca exata na Trie | O(m) |
| Busca por prefixo na Trie | O(m + N) — descer o prefixo + percorrer descendentes (≥ k) |
| Construção da Trie (vocabulário) | O(soma dos tamanhos das palavras de V) |
| Pré-processamento | O(tamanho total do texto) |
| Construção do índice invertido | O(n) médio |
| Consulta por palavra (Hash) | O(1) médio (+ O(d log d) para ordenar os d arquivos exibidos) |
| Consulta por prefixo completa | O(m + N + k·O(1)) |
| KMP por documento | O(L + m), L = tamanho do texto |
| Busca sequencial em lista de palavras | O(V · m) — comparação com a Trie abaixo |

## 8. Exemplos de consultas (saída real do programa, 6 documentos)
**Estatísticas:** 6 documentos · 1.316 palavras após tokenização · 858 termos distintos · 858 palavras na Trie (3.814 nós) · pré-processamento ≈ 1 ms · construção da Trie ≈ 2,5 ms · construção do índice ≈ 0,3 ms (tempos variam por execução/máquina).

| Consulta | Resultado | Tempo |
|---|---|---|
| Palavra `algoritmo` | algoritmos.txt, inteligencia_artificial.txt, processamento_textos.txt | ≈ 2–10 µs |
| Palavra `trie` | algoritmos.txt, processamento_textos.txt | ≈ 3 µs |
| Prefixo `prog` | programa (banco_dados, engenharia_software) · programar (inteligencia_artificial) · programas (engenharia_software, inteligencia_artificial) · programação (algoritmos, engenharia_software) | ≈ 20 µs |
| Prefixo `comp` | 20 palavras, incluindo compilador, complexidade, computação, computador... | ≈ 50–150 µs |
| Sequência (KMP) `tempo linear` | algoritmos.txt (1 ocorrência) | ≈ 1 ms |

Observação sobre os tempos: a consulta por palavra é praticamente constante (Hash), a por prefixo cresce com o número de resultados (O(m + N)) e o KMP cresce com o tamanho total do texto (O(n)) — o que condiz com a análise da Unidade 1. Para ver a diferença com clareza, use uma coleção grande.

## 9. Questões conceituais da Parte I
1. **Por que a Trie serve ao autocomplete?** Porque todas as palavras com um dado prefixo ficam sob um único nó; achar o prefixo custa O(m) e as sugestões são os descendentes, sem varrer o dicionário.
2. **Vantagem sobre a busca sequencial?** A busca sequencial compara a consulta com cada palavra (O(V·m)); na Trie o custo depende só do tamanho da consulta, não da quantidade de palavras armazenadas.
3. **Prefixos comuns?** Compartilham o mesmo caminho inicial de nós; só há ramificação onde as palavras diferem.
4. **Complexidade de buscar palavra de tamanho m?** O(m).
5. **Problema de memória?** Cada nó guarda um dicionário/vetor de filhos, e muitos nós têm um único filho (cadeias longas), gerando muitos nós e ponteiros — consumo alto de memória (aqui: 3.814 nós para 858 palavras).
6. **Trie comprimida?** (Radix tree / Patricia) funde cadeias de nós com um só filho em uma única aresta rotulada com uma substring. Reduz o número de nós para O(V) e economiza memória, mantendo busca proporcional a m.

## 10. Decisões de implementação
- Trie com `dict` de filhos (suporta acentos/Unicode sem tabela fixa) e `__slots__` para economizar memória.
- Percursos iterativos (sem recursão) para evitar estouro de pilha.
- Nenhum nome de arquivo no código: `os.listdir` descobre os `.txt`.
- Leitura robusta de codificação (UTF-8 com fallback Latin-1).
- Cada consulta é cronometrada com `time.perf_counter` e registrada num histórico.

## 11. Limitações
- Sem stemming/lematização: `algoritmo` e `algoritmos` são termos diferentes.
- Acentos são relevantes (`computacao` ≠ `computação`).
- Trie tradicional gasta bastante memória; seria possível usar Trie comprimida.
- O índice é só booleano (não guarda frequência nem ranking por relevância, como TF-IDF).
- Índice e Trie ficam em memória e são reconstruídos a cada execução (sem persistência em disco).
- KMP percorre todos os textos a cada consulta (não usa índice).
- Os documentos de teste são pequenos (~2.200 palavras); recomenda-se testar também com coleções maiores.
