import re
from abc import ABC, abstractmethod


class RegraValidacao(ABC):

    @abstractmethod
    def validar(self, valor: str) -> tuple[bool, str]: ...


class RegraVazio(RegraValidacao):

    def validar(self, valor: str) -> tuple[bool, str]:
        if not valor.strip():
            return False, "Nome não pode ser vazio!"
        return True, ""


class RegraFormatoNome(RegraValidacao):
    _PADRAO = re.compile(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]{3,}$')

    def validar(self, valor: str) -> tuple[bool, str]:
        if not self._PADRAO.match(valor):
            return False, "Nome deve conter pelo menos 3 letras e não pode conter números!"
        return True, ""


class ValidadorNome:

    def __init__(self):
        self._regras: tuple[RegraValidacao, ...] = (RegraVazio(), RegraFormatoNome())

    def validar(self, nome: str) -> tuple[bool, str]:
        for regra in self._regras:
            valido, mensagem = regra.validar(nome)
            if not valido:
                return False, mensagem
        return True, ""
