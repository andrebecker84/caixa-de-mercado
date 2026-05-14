import threading

class InputBridge:
    """Uma ponte sincronizada para o fluxo entre UseCases (Core) e Flet (UI)."""

    def __init__(self):
        self._event = threading.Event()
        self._value = None

    def wait(self) -> any:
        """Aguarda até que a ponte seja resolvida."""
        self._event.clear()
        self._event.wait()
        return self._value

    def resolve(self, value: any) -> None:
        """Envia um valor para a ponte e libera a espera."""
        self._value = value
        self._event.set()
