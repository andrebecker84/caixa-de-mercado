from app.core.ports import ClientePort
from app.shared.util import entrar_inteiro
from app.assets.estilos import *

class ClienteTerminalAdapter(ClientePort):
    def pedir_id(self) -> int:
        return entrar_inteiro(f"{busca}{azul} ID do Cliente (0 se não tiver): {reset}")

    def pedir_nome(self) -> str:
        return input(f"{input_emoticon}{azul} Nome do Novo Cliente: {reset}")

    def pedir_confirmacao_cadastro(self) -> bool:
        res = input(f"{input_emoticon}{amarelo} Cliente não encontrado. Deseja cadastrar? (S/N): {reset}").lower()
        return res == 's'

    def exibir_nome_invalido(self, mensagem: str) -> None:
        print(f"{cancela_emoticon}{vermelho} {mensagem}{reset}")

    def exibir_cliente_ja_cadastrado(self, nome: str, id_cliente: int) -> None:
        print(f"{ok}{verde} Cliente identificado: {nome} (ID: {id_cliente}){reset}")

    def exibir_cliente_registrado(self, nome: str, id_cliente: int) -> None:
        print(f"{ok}{verde} Cliente {nome} cadastrado com sucesso! ID: {id_cliente}{reset}")

    def exibir_erro(self, mensagem: str) -> None:
        print(f"{erro_emoticon}{vermelho} Erro: {mensagem}{reset}")
