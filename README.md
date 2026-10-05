# Mini Mecanismo de Busca — Trie + Índice Invertido + Hash (+ KMP)

Trabalho Prático A1 — Unidade 2 (Processamento e Busca de Textos)
Universidade Veiga de Almeida — Análise e Otimização de Sistemas

**Integrantes:** 
João Marcos Fierro
Geovanna Melo
Danielle Carvalho

## Requisitos
- Python 3.8 ou superior (testado no 3.12).
- Somente bibliotecas padrão (`re`, `os`, `time`, `argparse`, `tkinter`). Nada de Trie/índice/busca prontos.
- **Tkinter** (interface gráfica) vem com o Python no Windows e no macOS.
  No Linux (Ubuntu/Debian): `sudo apt install python3-tk`.

## Como executar
```bash
cd projeto
python main.py                 # INTERFACE GRÁFICA (padrão)
python main.py --cli           # Parte II em terminal (menu do enunciado)
python main.py --autocomplete  # Parte I em terminal (autocomplete)
python main.py --pasta OUTRA_PASTA --stopwords outro_arquivo.txt
```

## Usando a interface gráfica
| Aba | O que faz |
|---|---|
|Palavra | Busca exata no índice invertido (Hash) e lista os arquivos |
|Prefixo | Trie → palavras com o prefixo; índice invertido → documentos de cada uma |
|KMP | (Bônus) procura qualquer sequência de caracteres no texto original |
|Documentos | Lista os arquivos processados com contagens |
|Estatísticas | Todas as estatísticas obrigatórias + histórico com o tempo de cada consulta |
|Autocomplete | Parte I: sugestões enquanto digita, busca exata e inserção de novas palavras |

Para adicionar documentos: coloque novos `.txt` em `documentos/` e clique em *Recarregar*
(ou reinicie o programa). Nenhum nome de arquivo está fixo no código.

## Estrutura
```
projeto/
├── main.py              # ponto de entrada (GUI / --cli / --autocomplete)
├── gui.py               # interface gráfica (Tkinter)
├── cli.py               # Parte II em terminal
├── autocomplete.py      # Parte I em terminal
├── trie.py              # Trie implementada do zero (Parte I, reutilizada na Parte II)
├── preprocessamento.py  # minúsculas, pontuação, tokenização, stopwords, leitura de arquivos
├── indice_invertido.py  # índice invertido sobre dict (Hash)
├── kmp.py               # algoritmo KMP (bônus)
├── motor_busca.py       # integra tudo e mede os tempos
├── stopwords.txt        # lista de stopwords (editável)
├── palavras.txt         # palavras cadastradas para a Parte I
├── documentos/          # .txt usados nos testes
├── README.md
└── RELATORIO.md         # relatório técnico
```

## Observações
- Arquivos são lidos em UTF-8 (com ou sem BOM); se falhar, em Latin-1.
- A busca é sem distinção de maiúsculas/minúsculas, mas **com** acentos (`computação` ≠ `computacao`).
- Os 6 documentos de exemplo têm ~2.200 palavras. Para testes mais representativos, coloque
  textos maiores na pasta (livros em domínio público, artigos, etc.) — o programa escala sem alterações.
