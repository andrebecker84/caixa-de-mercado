from tqdm import tqdm


def barra_progresso(iteravel, descricao, cor="green", largura=80):
    return tqdm(iteravel, desc=descricao, colour=cor, ncols=largura)


def carregar_dados(sessao, funcao_carregar, icone, nome):
    list(barra_progresso(funcao_carregar(sessao), f"{icone} Carregando {nome}"))
    print()
