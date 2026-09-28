from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCriar(BaseModel):
    nome: str = Field(
        min_length=2, max_length=100, description="Nome do usuário", examples=["Maria Silva"]
    )
    email: EmailStr = Field(description="E-mail usado para fazer login", examples=["maria@email.com"])
    senha: str = Field(
        min_length=6, description="Senha com no mínimo 6 caracteres", examples=["senha123"]
    )


class UsuarioResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Identificador do usuário")
    nome: str
    email: EmailStr
    criado_em: datetime = Field(description="Data de cadastro (UTC)")


class Token(BaseModel):
    access_token: str = Field(description="Token JWT que deve ser enviado no header Authorization")
    token_type: str = Field(default="bearer", description="Tipo do token")
