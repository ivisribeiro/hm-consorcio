from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, usuarios, clientes, beneficios, unidades, empresas,
    utils, dashboard, relatorios, configuracoes,
    representantes, consultores, perfis
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(usuarios.router)
api_router.include_router(clientes.router)
api_router.include_router(beneficios.router)
api_router.include_router(unidades.router)
api_router.include_router(empresas.router)
api_router.include_router(representantes.router)
api_router.include_router(consultores.router)
api_router.include_router(utils.router)
api_router.include_router(dashboard.router)
api_router.include_router(relatorios.router)
api_router.include_router(configuracoes.router)
api_router.include_router(perfis.router)
