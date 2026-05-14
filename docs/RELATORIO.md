# Relatório Técnico de Refatoração — caixaMercado

**Autor:** André Luis Becker
**Data:** 18/03/2026
**Stack:** Python 3.14.3, SQLAlchemy 2.0.48, PyMySQL 1.1.2

---

## 1. Replace Dict with Dataclass — `ItemCarrinho`

**Localização:** `app/models/models.py`, `app/services/atendimento_service.py`

**Antes:**
```python
carrinho.append({
    "id_produto": produto.id_produto,
    "nome": produto.nome,
    "quantidade": quantidade,
    "preco_unitario": produto.preco,
    "subtotal": produto.preco * quantidade
})
```

**Depois:**
```python
@dataclass
class ItemCarrinho:
    id_produto: int
    nome: str
    quantidade: int
    preco_unitario: Decimal

    def __post_init__(self):
        if self.quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero.")
        if self.preco_unitario < Decimal("0"):
            raise ValueError("Preço unitário não pode ser negativo.")

    @property
    def subtotal(self) -> Decimal:
        return self.preco_unitario * self.quantidade
```

**Princípio aplicado:** SRP, Fail-Fast, encapsulamento Python.
**Justificativa:** O dicionário cru não oferece contrato, validação nem autodocumentação. A dataclass define o tipo do item de carrinho com campo computado via `@property`, validação no `__post_init__` e type hints em toda a assinatura. O subtotal deixa de ser calculado externamente e passa a ser responsabilidade do próprio objeto — eliminando duplicação e tornando o domínio expressivo.

---

## 2. Extract Function — `atendimento_service.py`

**Localização:** `app/services/atendimento_service.py`

**Antes:** `atender_cliente()` com 69 linhas misturando validação, `input()`, lógica de negócio e montagem de carrinho.

**Depois:** Função principal com 40 linhas delegando para:

| Função extraída | Responsabilidade |
|---|---|
| `_produto_disponivel()` | Busca e valida existência + estoque |
| `_quantidade_valida()` | Verifica se quantidade cabe no estoque acumulado |
| `_confirmar_adicao()` | Captura confirmação do operador para um item |
| `_confirmar_compra()` | Captura confirmação final da compra |
| `_processar_item()` | Orquestra uma iteração completa do loop de seleção |

**Princípio aplicado:** SRP, Extract Function (Fowler), funções com < 20 linhas.
**Justificativa:** Cada função extrai um bloco com intenção única e nome descritivo. O loop principal passa a expressar a intenção do fluxo em vez de detalhar a implementação de cada passo.

---

## 3. Move Function — subtotal para `ItemCarrinho`

**Localização:** `app/services/atendimento_service.py` → `app/models/models.py`

**Antes:**
```python
subtotal = produto.preco * quantidade
carrinho.append({..., "subtotal": subtotal})
total += subtotal
```

**Depois:**
```python
item = ItemCarrinho(produto.id_produto, produto.nome, quantidade, produto.preco)
total += item.subtotal  # calculado pelo próprio objeto
```

**Princípio aplicado:** Move Method (Fowler), coesão de domínio.
**Justificativa:** O cálculo de subtotal pertence ao item de carrinho, não ao serviço. Mover a responsabilidade elimina a variável temporária e garante que qualquer instância de `ItemCarrinho` sempre terá subtotal correto, sem depender de código externo.

---

## 4. Unify Type Access — `produto_service.py`

**Localização:** `app/services/produto_service.py`

**Antes:**
```python
produto = next(
    (p for p in lista_produtos if getattr(p, 'id_produto', p.get('id_produto')) == id_produto),
    None
)
estoque = getattr(produto, 'quantidade', produto.get('quantidade'))
```

**Depois:**
```python
produto = next((p for p in lista_produtos if p.id_produto == id_produto), None)
if quantidade > produto.quantidade:
    ...
```

**Princípio aplicado:** DRY, KISS, eliminação de dualidade de tipo.
**Justificativa:** O acesso via `getattr` com fallback para `.get()` indica que o código suportava simultaneamente objetos SQLAlchemy e dicionários — um contrato implícito e frágil. O fluxo real sempre passa objetos `Produto`. Eliminar a dualidade torna o tipo explícito e remove complexidade sem razão técnica.

---

## 5. Move Import — `cliente_service.py`

**Localização:** `app/services/cliente_service.py`

**Antes:**
```python
def obter_lista_clientes(sessao):
    try:
        from app.controller.cliente_controller import listar_clientes as listar_clientes_controller
        return listar_clientes_controller(sessao)
```

**Depois:**
```python
from app.controller.cliente_controller import listar_clientes, validar_ou_cadastrar_cliente

def obter_lista_clientes(sessao):
    try:
        return listar_clientes(sessao)
```

**Princípio aplicado:** Clean Code, ausência de import lazy sem justificativa técnica.
**Justificativa:** Import dentro de função oculta dependências, dificulta análise estática e penaliza performance na primeira chamada. Não há dependência circular entre `cliente_service` e `cliente_controller`, portanto o import tardio não tinha razão de existir.

---

## 6. Inline Function — `caixa_service.py`

**Localização:** `app/services/caixa_service.py`

**Antes:**
```python
def menu_caixa():
    exibir_menu_caixa()

def entrar_opcao_caixa():
    return entrar_opcao(menu_caixa, [INICIAR_ATENDIMENTO, FECHAR_CAIXA])

def fechar_caixa(sessao):
    ...
```

**Depois:**
```python
def fechar_caixa(sessao):
    ...
```

**Princípio aplicado:** Inline Function (Fowler), YAGNI.
**Justificativa:** `menu_caixa()` e `entrar_opcao_caixa()` não tinham callers — `sistema_controller.py` chamava `entrar_opcao(exibir_menu_caixa, [1, 2])` diretamente. Funções que apenas delegam sem adicionar valor são ruído. Removê-las reduz a superfície de API do módulo.

---

## 7. Extract Function por Responsabilidade — `sistema_service.py`

**Localização:** `app/services/sistema_service.py`

**Antes:** `inicializar_banco()` com 27 linhas misturando conexão, criação de tabelas, seed e recuperação de erro.

**Depois:**

| Função extraída | Responsabilidade |
|---|---|
| `_criar_tabelas(sessao)` | Cria tabelas via `create(checkfirst=True)` |
| `_popular_se_vazio(sessao)` | Executa seed apenas se banco vazio |
| `_criar_banco_e_popular(conexao)` | Recuperação: cria schema + seed em banco novo |

**Princípio aplicado:** SRP, Extract Function (Fowler).
**Justificativa:** Inicialização de banco envolve três responsabilidades distintas: verificar/criar estrutura, popular dados iniciais e recuperar de ausência total do banco. Separar cada uma em função nomeada permite testar e raciocinar sobre cada etapa individualmente e torna o fluxo de `inicializar_banco()` legível como sequência de intenções.

Adicionalmente, o import lazy de `fechar_caixa` dentro de `finalizar_sistema()` foi movido para o nível de módulo, eliminando a dependência circular aparente que não existia.

---

---

## 8. Extract View — I/O extraída de controller e service

**Localização:** `app/controller/cliente_controller.py`, `app/services/atendimento_service.py` → `app/views/cliente_view.py`, `app/views/atendimento_view.py`

**Antes:**
```python
# dentro de cliente_controller.py
id_cliente = int(input(f"{azul} ID do cliente: {reset}"))
print(f"{ok}{verde} Cliente registrado: {nome}{reset}")

# dentro de atendimento_service.py
id_produto = int(input(f"{azul} ID do produto: {reset}"))
print(f"{ok}{verde} {item.nome} adicionado ao carrinho.{reset}")
```

**Depois:**
```python
# cliente_view.py
def pedir_id_cliente() -> int:
    return int(input(f"{azul} ID do cliente: {reset}"))

def exibir_cliente_registrado(nome: str, id_cliente: int):
    print(f"{ok}{verde} Cliente {nome} (ID {id_cliente}) cadastrado.{reset}")

# atendimento_view.py
def pedir_id_produto() -> int:
    return int(input(f"{azul} ID do produto: {reset}"))

def exibir_item_adicionado(nome: str):
    print(f"{ok}{verde} {nome} adicionado ao carrinho.{reset}")
```

**Princípio aplicado:** SRP, separação de camadas, Extract Function (Fowler).
**Justificativa:** Controllers misturando `input()` e `print()` com lógica de orquestração violam SRP e impedem testes unitários de qualquer função sem simular o terminal. A extração para views mantém o contrato da camada: view só apresenta e coleta; service só processa; controller só orquestra.

---

## 9. Move Function — view sem acesso a dados

**Localização:** `app/views/sistema_view.py`, `app/views/produto_view.py`

**Antes:**
```python
# sistema_view.py importava e chamava services diretamente
def carregar_dados_msg(sessao):
    list(barra_progresso(ler_produtos(sessao), "Carregando produtos"))
    list(barra_progresso(listar_clientes(sessao), "Carregando clientes"))

# produto_view.py importava controller
from app.controller.produto_controller import produtos_sem_estoque, produtos_disponiveis

def verificar_estoque():
    sem_estoque = produtos_sem_estoque(sessao)
    ...
```

**Depois:**
```python
# sistema_view.py — apenas display puro
def exibir_banco_inicializado():
    print(f"{ok}{verde} Banco de dados inicializado com sucesso!{reset}\n")

def exibir_carregando_dados():
    print(f"{carregando}{azul} Carregando dados iniciais...{reset}\n")

# produto_view.py — recebe dados prontos por parâmetro
def verificar_estoque(sem_estoque: list, disponiveis: list | None = None):
    ...
```

**Princípio aplicado:** SRP, separação de camadas, Move Function (Fowler).
**Justificativa:** View acessando banco viola a separação de camadas — a view não pode saber como nem de onde os dados vêm. A refatoração inverte a dependência: quem tem a sessão (controller/service) busca os dados e os entrega à view como parâmetros simples.

---

## 10. Fix Session Lifecycle — sessão fechada pelo ponto correto

**Localização:** `app/services/caixa_service.py`, `app/services/sistema_service.py`

**Antes:**
```python
# caixa_service.py — fechava a sessão dentro de um service aninhado
def fechar_caixa(sessao):
    ...
    sessao.close()  # premature close — sistema_service ainda precisava da sessão
```

**Depois:**
```python
# caixa_service.py — opera normalmente sem fechar
def fechar_caixa(sessao):
    compras = calcular_totais_do_dia(sessao)
    ...
    verificar_estoque(sem_estoque, disponiveis)

# sistema_service.py — único responsável pelo ciclo de vida
def finalizar_sistema(sessao):
    try:
        sessao.commit()
        fechar_caixa(sessao)
    except Exception:
        sessao.rollback()
        raise
    finally:
        sessao.close()
```

**Princípio aplicado:** SRP, gerenciamento de recurso em ponto único, RAII adaptado a Python.
**Justificativa:** A sessão SQLAlchemy é um recurso compartilhado. Fechá-la dentro de um service que não a abriu viola SRP e cria dependência de ordem de execução entre services. O único responsável por abrir e fechar a sessão é `sistema_service`, que detém o contexto de todo o ciclo de atendimento.

---

## 11. Remove Dead Code — comentários residuais em `conexao_db.py`

**Localização:** `database/auth/conexao_db.py`

**Antes:**
```python
self.session = sessionmaker(bind=self.engine)()
# print("Conexão com o banco de dados estabelecida com sucesso!\n")
return self.session

def desconectar_banco(self, session):
    if session:
        session.close()
        # print("\nConexão com o banco de dados encerrada com sucesso!")
```

**Depois:** linhas comentadas removidas.

**Princípio aplicado:** Clean Code, Anti-Boilerplate.
**Justificativa:** Código comentado é ruído. Não documenta, não executa e cria dúvida sobre se foi intencionalmente desativado ou esquecido. Controle de versão preserva o histórico — não há razão para manter `print()` comentados no arquivo.

---

## 12. Repository Pattern — isolamento da persistência

**Localização:** `app/domain/repositories/` (interfaces) + `app/infrastructure/repositories/` (implementações)

**Antes:**
```python
# espalhado em controller/atendimento_controller.py, controller/produto_controller.py, etc.
def listar_produtos_disponiveis(sessao):
    return sessao.query(Produto).filter(Produto.quantidade > 0).all()

def registrar_compra(sessao, id_cliente, itens):
    nova_compra = Compra(...)
    sessao.add(nova_compra)
    ...
    sessao.commit()
```

**Depois:**
```python
# app/domain/repositories/produto_repository.py
class ProdutoRepository(ABC):
    @abstractmethod
    def disponiveis(self) -> list[Produto]: ...

# app/infrastructure/repositories/produto_repository.py
class SQLAlchemyProdutoRepository(ProdutoRepository):
    def disponiveis(self) -> list[Produto]:
        return self._sessao.query(Produto).filter(Produto.quantidade > 0).all()

# app/use_cases/atendimento_use_case.py
class AtendimentoUseCase:
    def __init__(self, produto_repo: ProdutoRepository, compra_repo: CompraRepository):
        self._produto_repo = produto_repo
        self._compra_repo = compra_repo
```

**Princípio aplicado:** Repository Pattern (DDD), Clean Architecture, Dependency Inversion (SOLID D).
**Justificativa:** Antes, os casos de uso dependiam diretamente do SQLAlchemy — qualquer mudança de ORM exigiria reescrever lógica de negócio. Com o repositório, o caso de uso conhece apenas a interface abstrata. A implementação concreta é injetada pelo handler, invertendo a dependência. Os use cases passam a ser testáveis com qualquer implementação in-memory.

---

## 13. Command Pattern — dispatch de menu via objetos executáveis

**Localização:** `app/handlers/`, `app/controller/sistema_controller.py`

**Antes:**
```python
if opcao == 1:
    cliente = validar_ou_cadastrar_cliente(sessao)
    if cliente:
        atender_cliente(sessao, cliente.nome, cliente.id_cliente)
    else:
        exibir_cancelamento()
elif opcao == 2:
    exibir_fechando_caixa()
    break
```

**Depois:**
```python
# app/handlers/comando.py
class Comando(ABC):
    @abstractmethod
    def executar(self) -> None: ...

# sistema_controller.py
comandos = {
    1: AtendimentoHandler(sessao),
    2: FecharCaixaHandler(sessao),
}
while True:
    opcao = entrar_opcao(exibir_menu_caixa, list(comandos.keys()))
    if opcao == 2:
        exibir_fechando_caixa()
        break
    comandos[opcao].executar()
```

**Princípio aplicado:** Command Pattern (GoF), OCP.
**Justificativa:** O `if/elif` no loop principal viola OCP — adicionar uma opção exige modificar o controlador. Com o `dict` de `Comando`, adicionar a opção 3 é criar um novo handler e registrá-lo, sem alterar o despacho. O controlador não conhece o que cada comando faz; apenas sabe chamar `executar()`.

---

## 14. Strategy Pattern — validação de nome como composição de regras

**Localização:** `app/domain/validators/nome_validator.py`

**Antes:**
```python
def validar_nome(nome):
    if not nome.strip():
        return False, "Nome não pode ser vazio!"
    if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]{3,}$', nome):
        return False, "Nome deve conter pelo menos 3 letras e não pode conter números!"
    return True, ""
```

**Depois:**
```python
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
    _regras = [RegraVazio(), RegraFormatoNome()]
    def validar(self, nome: str) -> tuple[bool, str]:
        for regra in self._regras:
            valido, mensagem = regra.validar(nome)
            if not valido:
                return False, mensagem
        return True, ""
```

**Princípio aplicado:** Strategy Pattern (GoF), SRP, OCP.
**Justificativa:** A função procedural `validar_nome` acumulava múltiplas regras no mesmo bloco. Cada `RegraValidacao` é responsável por uma única verificação. `ValidadorNome` é um compositor — não conhece as regras, apenas as itera. Adicionar uma regra nova (e.g., tamanho máximo) é criar uma classe independente e registrá-la na lista, sem modificar as existentes.

---

## 15. Ports & Adapters — use cases desacoplados da I/O

**Localização:** `app/core/ports.py`, `app/core/*_use_case.py`, `app/views/*_adapter.py`, `app/flet/adapters/*_adapter.py`

**Antes:**
```python
# atendimento_use_case.py — importava diretamente funções de view
from app.views.atendimento_view import (
    confirmar_adicao, confirmar_compra, exibir_carrinho,
    exibir_inicio_atendimento, pedir_id_produto, pedir_quantidade, ...
)

class AtendimentoUseCase:
    def __init__(self, produto_repo, compra_repo):   # sem porta
        ...
    def atender(self, cliente_nome, cliente_id):
        exibir_inicio_atendimento(cliente_nome)      # acoplado à view de terminal
        id_produto = pedir_id_produto()              # acoplado ao terminal
```

**Depois:**
```python
# app/core/ports.py
class AtendimentoPort(ABC):
    @abstractmethod
    def exibir_inicio(self, cliente_nome: str) -> None: ...
    @abstractmethod
    def pedir_id_produto(self) -> int: ...
    @abstractmethod
    def confirmar_compra(self) -> bool: ...
    ...

# app/core/atendimento_use_case.py — zero import de view
class AtendimentoUseCase:
    def __init__(self, produto_repo, compra_repo, porta: AtendimentoPort):
        self._porta = porta

    def atender(self, cliente_nome, cliente_id):
        self._porta.exibir_inicio(cliente_nome)      # interface agnóstica de I/O
        id_produto = self._porta.pedir_id_produto()  # terminal ou Flet — indiferente

# app/views/atendimento_adapter.py — adaptador terminal
class AtendimentoTerminalAdapter(AtendimentoPort):
    def exibir_inicio(self, cliente_nome):
        exibir_inicio_atendimento(cliente_nome)      # delega para print()

# app/flet/adapters/atendimento_adapter.py — adaptador Flet
class AtendimentoFletAdapter(AtendimentoPort):
    def exibir_inicio(self, cliente_nome):
        self._ctrl.set_content(...)                  # delega para ft.Page
```

**Princípio aplicado:** Ports & Adapters (Hexagonal Architecture), DIP (SOLID D), SRP.
**Justificativa:** Use cases importando módulos de view criam acoplamento direto entre lógica de negócio e meio de apresentação — violação de DIP. Com o padrão Ports & Adapters, os use cases dependem apenas de abstrações (`AtendimentoPort`, `ClientePort`, `CaixaPort`). Implementações concretas são injetadas pelos handlers no momento da composição. O resultado imediato foi a adição da interface Flet sem alterar uma única linha de lógica de negócio ou de infraestrutura.

---

## 16. Interface gráfica Flet com bridge de threading

**Localização:** `app/flet/bridge.py`, `app/flet/adapters/`, `app/flet/pages/`, `app/flet/app.py`

**Problema:** Os use cases executam fluxo síncrono e bloqueante — chamam `porta.pedir_id()` e só avançam quando recebem uma resposta. Flet é event-driven: callbacks de botão retornam imediatamente e o event loop não pode ser bloqueado.

**Solução — `InputBridge` com `threading.Event`:**
```python
# app/flet/bridge.py
class InputBridge:
    def __init__(self):
        self._event = threading.Event()
        self._result = None

    def wait(self):
        """Bloqueia a thread do use case até resolve() ser chamado."""
        self._event.clear()
        self._event.wait()
        return self._result

    def resolve(self, value) -> None:
        """Chamado pelo callback Flet na thread principal."""
        self._result = value
        self._event.set()
```

**Fluxo de execução:**
```
Thread daemon (use case)         Thread principal (Flet)
────────────────────────         ───────────────────────────────
AtendimentoUseCase.atender()
  porta.pedir_id_produto()
    ctrl.set_content(form)   →   page.update() — renderiza formulário
    bridge.wait()            →   bloqueia
                                 usuário digita e clica "Confirmar"
                                 button.on_click()
                             →   bridge.resolve(int(tf.value))
    ← retorna int            ←   event.set()
  continua lógica de negócio
```

**Componentes Flet:**

| Componente | Responsabilidade |
|---|---|
| `theme.py` | Paleta dark/light, sombras `ft.BoxShadow` duplo, `border_radius`, animações |
| `controller.py` | `PageController` — `set_content`, `append_content`, `notify` (SnackBar), factories de widgets |
| `pages/splash.py` | Carregamento com `ProgressRing` e `inicializar_banco` em thread daemon |
| `pages/menu.py` | Cards com hover animado via `on_hover` + `ft.animation.Animation(180ms)` |
| `adapters/atendimento_adapter.py` | Layout dois painéis: tabela de produtos (esquerda) + carrinho dinâmico + input (direita) |
| `adapters/cliente_adapter.py` | Cards sequenciais: ID → confirmação → nome, cada passo bloqueia no bridge |
| `adapters/caixa_adapter.py` | Relatório de fechamento em cards empilhados, sem input bloqueante |

**Design system:**
- Dark: `#0D0D1A` background, `#7C6FCD` violet, `#00C9A7` teal accent
- Light: `#F5F5F7` (macOS), `#5856D6` Apple purple
- Sombras: `blur_radius=28` + `blur_radius=6` (camadas, estilo macOS)
- `border_radius=16` cards, `12` botões, `10` inputs
- Toggle dark/light no header via `ft.IconButton`

**Princípio aplicado:** Adapter Pattern (GoF), separação entre lógica de domínio e meio de apresentação.
**Justificativa:** A troca completa da interface de terminal para GUI (Flutter/Material Design 3) foi realizada sem modificar nenhum use case, repositório ou entidade de domínio. A arquitetura hexagonal, validada na prática, demonstra que a dependência entre camadas flui sempre de fora para dentro: a UI conhece os use cases, os use cases conhecem apenas as ports, o domínio não conhece ninguém.

---

## 17. Docker Compose unificado — redes segregadas e profiles

**Localização:** `docker-compose.yml` (raiz), substitui `docker/docker-compose.yml` e `docker/docker-compose.flet.yml`

**Antes:** dois arquivos compose independentes, sem isolamento de rede, todos os serviços sempre ativos e sem separação por ambiente:

```yaml
# docker/docker-compose.flet.yml — serviços sempre expostos, flat network implícita
services:
  db:
    image: mysql:8.4.8
    ...
  flet:
    ...
    ports:
      - "8550:8550"
  test:
    ...
```

**Depois:** compose unificado com duas redes e profiles para ativação sob demanda:

```yaml
services:
  db:
    networks: [backend]          # banco nunca exposto ao frontend

  flet:
    networks: [backend, frontend] # único serviço com acesso externo ao app
    ports: ["8550:8550"]

  app:
    networks: [backend]
    profiles: [cli]              # CLI interativa — ativada explicitamente

  test:
    networks: [backend]
    profiles: [test]             # pytest — sem interferência no compose padrão

  adminer:
    networks: [backend, frontend]
    ports: ["8081:8080"]
    profiles: [dev]              # inspeção do banco apenas em ambiente de dev

networks:
  backend:  {driver: bridge}     # isolado — db, app, test não são acessíveis de fora
  frontend: {driver: bridge}     # flet e adminer — visíveis externamente
```

**Topologia de redes:**

```
                    ┌──────────────────────┐
                    │  rede: frontend      │
                    │  (acesso externo)    │
                    └──────────┬───────────┘
                               │
              ┌────────────────┴────────────────┐
              │  flet — porta 8550              │
              │  adminer — porta 8081 [dev]     │
              └────────────────┬────────────────┘
                               │
                    ┌──────────┴───────────┐
                    │  rede: backend       │
                    │  (isolada, interna)  │
                    └──────────┬───────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   db — MySQL 8.4.8     app — CLI [cli]      test — pytest [test]
```

**Profiles:**

| Profile | Serviços ativos | Comando |
|---|---|---|
| *(nenhum)* | `db` + `flet` | `docker compose up --build` |
| `cli` | + `app` (stdin/tty interativo) | `docker compose --profile cli run --rm app` |
| `test` | + `test` (pytest + htmlcov) | `docker compose --profile test run --rm test` |
| `dev` | + `adminer` | `docker compose --profile dev up adminer` |

**Princípio aplicado:** separação de responsabilidades, princípio do menor privilégio, eliminação de redundância.
**Justificativa:** Dois arquivos compose com conteúdo sobreposto violam DRY e exigem manutenção duplicada de healthchecks, variáveis e volumes. A consolidação elimina a redundância. A segregação por redes aplica o princípio do menor privilégio: o banco não é alcançável pela rede pública — apenas por serviços na rede `backend`. Profiles evitam que serviços opcionais (CLI interativa, testes, adminer) consumam recursos em subidas padrão.

---

## Métricas

| Indicador | Antes | Depois |
|---|---|---|
| Maior função (linhas) | 69 (`atender_cliente`) | 40 (`atender_cliente`) |
| Dicts como objetos de domínio | 2 (`carrinho`, `cancelados`) | 0 |
| Imports lazy sem justificativa | 2 | 0 |
| Funções wrapper sem valor | 2 | 0 |
| `input()` fora da camada view | 4+ | 0 |
| `print()` em services | 5+ | 0 |
| Views com acesso direto a DB | 1 | 0 |
| Sessão fechada fora de `sistema_service` | 1 | 0 |
| `sessao.query()` fora de repositórios | 12+ | 0 |
| `if/elif` de menu em controlador | 1 bloco | 0 (Command dispatch) |
| Regras de validação embutidas em função | 1 função procedural | `ValidadorNome` + 2 estratégias |
| Imports de view dentro de use cases | 3 módulos | 0 (Ports & Adapters) |
| Interfaces de I/O intercambiáveis | 0 | 2 (terminal + Flet) |
| Arquivos docker-compose | 2 (sobrepostos) | 1 (unificado, profiles + redes) |
| Redes Docker isoladas | 0 | 2 (`backend`, `frontend`) |
| Cobertura de testes | 0% | cobertura de domínio crítico |
| Testes determinísticos | 0 | 6 |
| Propriedades hypothesis | 0 | 3 |

---

## Referências

- MARTIN, Robert C. *Clean Code: A Handbook of Agile Software Craftsmanship*. 2. ed.
- FOWLER, Martin. *Refactoring: Improving the Design of Existing Code*.
- Documentação oficial: Python 3.14, SQLAlchemy 2.0, pytest 9.x, hypothesis 6.x
