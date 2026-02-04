/**
 * Extrai mensagem de erro da resposta da API
 * @param {Error} error - Erro do axios
 * @param {string} defaultMessage - Mensagem padrão se não conseguir extrair
 * @returns {string} Mensagem de erro formatada
 */
export const getErrorMessage = (error, defaultMessage = 'Erro ao processar requisição') => {
  const detail = error.response?.data?.detail
  
  if (!detail) {
    return defaultMessage
  }
  
  // Se detail é um array (erros de validação do Pydantic)
  if (Array.isArray(detail)) {
    return detail.map(d => d.msg || d.message || JSON.stringify(d)).join(', ')
  }
  
  // Se detail é uma string
  if (typeof detail === 'string') {
    return detail
  }
  
  // Se detail é um objeto
  if (typeof detail === 'object') {
    return detail.msg || detail.message || JSON.stringify(detail)
  }
  
  return defaultMessage
}
