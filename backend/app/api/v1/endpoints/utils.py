from fastapi import APIRouter, HTTPException
import requests
import re

router = APIRouter(prefix="/utils", tags=["Utilitários"])


def validar_cpf(cpf: str) -> bool:
    """Valida CPF usando algoritmo oficial"""
    cpf = re.sub(r'\D', '', cpf)

    if len(cpf) != 11:
        return False

    # Verifica CPFs inválidos conhecidos
    if cpf in [str(i) * 11 for i in range(10)]:
        return False

    # Calcula primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if int(cpf[9]) != digito1:
        return False

    # Calcula segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    return int(cpf[10]) == digito2


def validar_cnpj(cnpj: str) -> bool:
    """Valida CNPJ usando algoritmo oficial"""
    cnpj = re.sub(r'\D', '', cnpj)

    if len(cnpj) != 14:
        return False

    if cnpj in [str(i) * 14 for i in range(10)]:
        return False

    # Primeiro dígito
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if int(cnpj[12]) != digito1:
        return False

    # Segundo dígito
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    return int(cnpj[13]) == digito2


@router.get("/validar-cpf/{cpf}")
async def validar_cpf_endpoint(cpf: str):
    """Valida um CPF"""
    cpf_limpo = re.sub(r'\D', '', cpf)

    if not validar_cpf(cpf_limpo):
        raise HTTPException(status_code=400, detail="CPF inválido")

    # Formata o CPF
    cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"

    return {
        "cpf": cpf_formatado,
        "valido": True,
        "message": "CPF válido"
    }


@router.get("/validar-cnpj/{cnpj}")
async def validar_cnpj_endpoint(cnpj: str):
    """Valida um CNPJ"""
    cnpj_limpo = re.sub(r'\D', '', cnpj)

    if not validar_cnpj(cnpj_limpo):
        raise HTTPException(status_code=400, detail="CNPJ inválido")

    # Formata o CNPJ
    cnpj_formatado = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"

    return {
        "cnpj": cnpj_formatado,
        "valido": True,
        "message": "CNPJ válido"
    }


@router.get("/buscar-cep/{cep}")
async def buscar_cep(cep: str):
    """Busca endereço pelo CEP usando ViaCEP"""
    cep_limpo = re.sub(r'\D', '', cep)

    if len(cep_limpo) != 8:
        raise HTTPException(status_code=400, detail="CEP inválido")

    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=10)
        data = response.json()

        if "erro" in data:
            raise HTTPException(status_code=404, detail="CEP não encontrado")

        return {
            "cep": data.get("cep", "").replace("-", ""),
            "logradouro": data.get("logradouro", ""),
            "complemento": data.get("complemento", ""),
            "bairro": data.get("bairro", ""),
            "cidade": data.get("localidade", ""),
            "estado": data.get("uf", ""),
            "ibge": data.get("ibge", "")
        }
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Serviço de CEP indisponível")
