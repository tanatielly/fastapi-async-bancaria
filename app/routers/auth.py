from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.database import SessaoDep
from app.models import Usuario
from app.schemas.usuario import Token, UsuarioCriar, UsuarioResposta
from app.seguranca import (
    UsuarioAtual,
    criar_token_acesso,
    gerar_hash_senha,
    verificar_senha,
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/cadastro", response_model=UsuarioResposta, status_code=status.HTTP_201_CREATED)
async def cadastrar_usuario(dados: UsuarioCriar, sessao: SessaoDep):
    resultado = await sessao.execute(select(Usuario).where(Usuario.email == dados.email))
    if resultado.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário cadastrado com esse e-mail.",
        )

    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=gerar_hash_senha(dados.senha),
    )
    sessao.add(usuario)
    await sessao.commit()
    await sessao.refresh(usuario)
    return usuario


@router.post("/login", response_model=Token)
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], sessao: SessaoDep):
    # o formulário do OAuth2 chama o campo de "username", aqui usamos o e-mail
    resultado = await sessao.execute(select(Usuario).where(Usuario.email == form.username))
    usuario = resultado.scalar_one_or_none()

    if usuario is None or not verificar_senha(form.password, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(access_token=criar_token_acesso(usuario.id))


@router.get("/me", response_model=UsuarioResposta)
async def usuario_logado(usuario: UsuarioAtual):
    return usuario
