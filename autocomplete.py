import os
import time

from trie import Trie
from preprocessamento import ler_arquivo
from motor_busca import formatar_tempo

ARQUIVO_PALAVRAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "palavras.txt")


def carregar_trie(caminho=ARQUIVO_PALAVRAS):
    trie = Trie()
    if os.path.isfile(caminho):
        for linha in ler_arquivo(caminho).splitlines():
            trie.inserir(linha.strip().lower())
    return trie


def executar():
    trie = carregar_trie()
    while True:
        print("\n" + "=" * 36)
        print("AUTOCOMPLETE COM TRIE")
        print("=" * 36)
        print(f"Palavras cadastradas: {len(trie)}\n")
        print("1 - Buscar palavra\n2 - Buscar por prefixo\n3 - Inserir nova palavra\n4 - Sair")
        opcao = input("\nEscolha uma opção: ").strip()
        if opcao == "1":
            p = input("Digite a palavra: ").strip().lower()
            t0 = time.perf_counter()
            achou = trie.buscar(p)
            dt = time.perf_counter() - t0
            print(f"'{p}' {'EXISTE' if achou else 'NÃO existe'} na Trie. ({formatar_tempo(dt)})")
        elif opcao == "2":
            p = input("Digite o prefixo: ").strip().lower()
            t0 = time.perf_counter()
            achadas = trie.buscar_prefixo(p)
            dt = time.perf_counter() - t0
            if achadas:
                print("Palavras encontradas:")
                for a in achadas:
                    print("  " + a)
            else:
                print("Nenhuma palavra encontrada.")
            print(f"({len(achadas)} resultado(s) em {formatar_tempo(dt)})")
        elif opcao == "3":
            p = input("Nova palavra: ").strip().lower()
            if p and trie.inserir(p):
                print(f"'{p}' inserida com sucesso.")
            else:
                print("Palavra vazia ou já cadastrada.")
        elif opcao == "4":
            print("Até logo!")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    executar()
