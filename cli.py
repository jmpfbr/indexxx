from motor_busca import MotorBusca, formatar_tempo


def mostrar_estatisticas(motor):
    print("\n--- ESTATÍSTICAS ---")
    for chave, valor in motor.estatisticas().items():
        print(f"{chave}: {valor}")


def executar(pasta="documentos", stopwords="stopwords.txt"):
    motor = MotorBusca(pasta, stopwords)
    motor.construir()
    while True:
        e = motor.estatisticas()
        print("\n" + "=" * 48)
        print("SISTEMA DE BUSCA EM DOCUMENTOS")
        print("=" * 48)
        print(f"Documentos processados: {e['Documentos processados']}")
        print(f"Total de palavras: {e['Total de palavras (após tokenização)']}")
        print(f"Termos distintos: {e['Termos distintos (vocabulário)']}\n")
        print("1 - Buscar palavra\n2 - Buscar por prefixo\n3 - Buscar sequência nos documentos (KMP)")
        print("4 - Listar documentos\n5 - Exibir estatísticas\n6 - Sair")
        opcao = input("\nEscolha uma opção: ").strip()
        if opcao == "1":
            docs, dt = motor.buscar_palavra(input("Digite a palavra: "))
            if docs:
                print(f"Encontrada em {len(docs)} arquivo(s):")
                for d in docs:
                    print("- " + d)
            else:
                print("Palavra não encontrada.")
            print(f"Tempo da consulta: {formatar_tempo(dt)}")
        elif opcao == "2":
            res, dt = motor.buscar_prefixo(input("Digite o prefixo: "))
            if res:
                print("Palavras encontradas:")
                for palavra, docs in res:
                    print(f"  {palavra:<22} -> {', '.join(docs)}")
            else:
                print("Nenhuma palavra com esse prefixo.")
            print(f"Tempo da consulta: {formatar_tempo(dt)}")
        elif opcao == "3":
            res, dt = motor.buscar_sequencia(input("Digite a sequência: "))
            if res:
                for nome, qtd, trecho in res:
                    print(f"- {nome} ({qtd} ocorrência(s)): ...{trecho}...")
            else:
                print("Sequência não encontrada.")
            print(f"Tempo da consulta: {formatar_tempo(dt)}")
        elif opcao == "4":
            for nome, info in motor.info_docs.items():
                print(f"- {nome}: {info['palavras']} palavras, {info['distintas']} distintas")
        elif opcao == "5":
            mostrar_estatisticas(motor)
        elif opcao == "6":
            print("Até logo!")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    executar()
