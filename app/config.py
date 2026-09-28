from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracoes(BaseSettings):
    # os valores podem ser sobrescritos por variaveis de ambiente ou pelo arquivo .env
    url_banco: str = "sqlite+aiosqlite:///./banco.db"
    chave_secreta: str = "troque-essa-chave-em-producao"
    algoritmo: str = "HS256"
    minutos_expiracao_token: int = 30

    model_config = SettingsConfigDict(env_file=".env")


configuracoes = Configuracoes()
