import argparse
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)


def principal():
    ap = argparse.ArgumentParser(description="Mini mecanismo de busca (Trie + Índice Invertido + Hash + KMP)")
    ap.add_argument("--pasta", default=os.path.join(BASE, "documentos"))
    ap.add_argument("--stopwords", default=os.path.join(BASE, "stopwords.txt"))
    args = ap.parse_args()

    import gui
    gui.executar(args.pasta, args.stopwords)


if __name__ == "__main__":
    principal()
