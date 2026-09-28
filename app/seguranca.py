from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from app.config import configuracoes
from app.database import SessaoDep
from app.models import Usuario

hash_senha = PasswordHash.recommended()

# o tokenUrl é a rota de login, assim o botão "Authorize" do Swagger funciona
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def gerar_hash_senha(senha: str) -> str:
    return hash_senha.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return hash_senha.verify(senha, senha_hash)


def criar_token_acesso(usuario_id: int) -> str:
    expira_em = datetime.now(timezone.utc) + timedelta(
        minutes=configuracoes.minutos_expiracao_token
    )
    payload = {"sub": str(usuario_id), "exp": expira_em}
    return jwt.encode(payload, configuracoes.chave_secreta, algorithm=configuracoes.algoritmo)


async def obter_usuario_atual(
    token: Annotated[str, Depends(oauth2_scheme)], sessao: SessaoDep
) -> Usuario:
    erro_credenciais = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, configuracoes.chave_secreta, algorithms=[configuracoes.algoritmo]
        )
        usuario_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise erro_credenciais

    usuario = await sessao.get(Usuario, usuario_id)
    if usuario is None:
        raise erro_credenciais

    return usuario


UsuarioAtual = Annotated[Usuario, Depends(obter_usuario_atual)]
