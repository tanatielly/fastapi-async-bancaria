# API Bancária Assíncrona com FastAPI

Projeto desenvolvido para o desafio **"API Bancária Assíncrona com FastAPI"** da DIO.

É uma API RESTful assíncrona para gerenciar **depósitos** e **saques** em contas correntes, com **extrato** e autenticação via **JWT**.

## Funcionalidades

- Cadastro de usuários e login com geração de token JWT
- Abertura de contas correntes (um usuário pode ter várias contas)
- Cadastro de transações: depósito e saque
- Extrato da conta com o saldo atual e todas as transações
- Validações:
  - não aceita depósito nem saque com valor negativo ou zero
  - não deixa sacar mais do que o saldo da conta
  - cada usuário só consegue ver e movimentar as próprias contas
- Documentação automática com OpenAPI (Swagger e ReDoc)

## Tecnologias

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/) no modo assíncrono + SQLite ([aiosqlite](https://github.com/omnilib/aiosqlite))
- [Pydantic](https://docs.pydantic.dev/) para validação dos dados
- [PyJWT](https://pyjwt.readthedocs.io/) para os tokens JWT
- [pwdlib](https://frankie567.github.io/pwdlib/) (Argon2) para o hash das senhas
- [pytest](https://docs.pytest.org/) + [httpx](https://www.python-httpx.org/) para os testes

## Estrutura do projeto

```
app/
├── main.py          # cria a aplicação e registra as rotas
├── config.py        # configurações lidas do .env
├── database.py      # conexão assíncrona com o banco
├── seguranca.py     # hash de senha, geração e validação do JWT
├── models/          # tabelas do banco (Usuario, Conta, Transacao)
├── schemas/         # modelos Pydantic de entrada e saída
└── routers/         # rotas de auth, contas e transações
tests/               # testes automatizados
```

### Modelagem

```
Usuario 1 ──── N Conta 1 ──── N Transacao
```

- **Usuario**: nome, e-mail e senha (guardada com hash)
- **Conta**: agência, número, saldo e o usuário dono
- **Transacao**: tipo (`deposito` ou `saque`), valor, descrição e data, sempre ligada a uma conta

## Como rodar

Pré-requisito: Python 3.11 ou mais recente (usei o 3.13).

```bash
# clonar o repositório e entrar na pasta
git clone <url-do-repositorio>
cd fastapi-async-bancaria

# criar e ativar o ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac

# instalar as dependências
pip install -r requirements.txt

# (opcional) criar o .env a partir do exemplo e trocar a chave secreta
cp .env.example .env

# subir a API
uvicorn app.main:app --reload
```

A API fica em `http://127.0.0.1:8000`. O banco (`banco.db`) e as tabelas são criados sozinhos na primeira vez que a aplicação sobe.

### Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `URL_BANCO` | `sqlite+aiosqlite:///./banco.db` | URL de conexão com o banco |
| `CHAVE_SECRETA` | uma chave de exemplo | Chave usada para assinar o JWT (**troque em produção**) |
| `ALGORITMO` | `HS256` | Algoritmo do JWT |
| `MINUTOS_EXPIRACAO_TOKEN` | `30` | Tempo de validade do token |

Para gerar uma chave secreta:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Documentação

Com a API rodando:

- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Testando pelo Swagger

1. Em `POST /auth/cadastro`, cadastre um usuário
2. Clique em **Authorize** (cadeado no topo da página), coloque o **e-mail no campo username** e a senha
3. Em `POST /contas`, abra uma conta e anote o `id` que voltar
4. Em `POST /contas/{conta_id}/transacoes`, faça um depósito:
   ```json
   { "tipo": "deposito", "valor": "500.00", "descricao": "Salário" }
   ```
5. Tente um saque maior que o saldo pra ver a validação funcionando
6. Em `GET /contas/{conta_id}/extrato`, veja o extrato

## Endpoints

| Método | Rota | Autenticação | Descrição |
|---|---|:---:|---|
| POST | `/auth/cadastro` | | Cadastra um usuário |
| POST | `/auth/login` | | Faz login e retorna o token JWT |
| GET | `/auth/me` | ✔ | Dados do usuário logado |
| POST | `/contas` | ✔ | Abre uma conta corrente |
| GET | `/contas` | ✔ | Lista as contas do usuário |
| GET | `/contas/{conta_id}` | ✔ | Consulta uma conta e o saldo |
| POST | `/contas/{conta_id}/transacoes` | ✔ | Registra um depósito ou saque |
| GET | `/contas/{conta_id}/extrato` | ✔ | Exibe o extrato da conta |

### Exemplo de extrato

```json
{
  "conta": {
    "id": 1,
    "agencia": "0001",
    "numero": "915666",
    "saldo": "379.25",
    "criada_em": "2026-09-28T22:42:47.081516"
  },
  "transacoes": [
    { "id": 1, "conta_id": 1, "tipo": "deposito", "valor": "500.00", "descricao": "Salario", "criada_em": "2026-09-28T22:42:47.103201" },
    { "id": 2, "conta_id": 1, "tipo": "saque", "valor": "120.75", "descricao": null, "criada_em": "2026-09-28T22:42:47.145872" }
  ]
}
```

### Códigos de resposta

| Código | Quando acontece |
|---|---|
| `400` | Saque maior que o saldo da conta |
| `401` | Token ausente, inválido ou expirado, ou login com senha errada |
| `404` | Conta não existe ou pertence a outro usuário |
| `409` | E-mail já cadastrado |
| `422` | Dados inválidos (ex.: valor negativo ou zero, senha curta, tipo de transação inválido) |

> **Obs.:** os valores em dinheiro usam `Decimal` em vez de `float` para não ter problema de arredondamento, por isso eles aparecem como texto no JSON (`"150.00"`). Na entrada dá pra mandar tanto número (`150`) quanto texto (`"150.00"`).

## Testes

```bash
pytest -v
```

Os testes usam um banco SQLite em memória, criado do zero em cada teste, então não mexem no `banco.db`.

## Próximos passos

Coisas que eu gostaria de adicionar depois:

- Migrations com Alembic (hoje as tabelas são criadas com `create_all`)
- Usar PostgreSQL e Docker
- Paginação e filtro por período no extrato
- Transferência entre contas
- Tratar melhor saques simultâneos na mesma conta (lock no banco)
