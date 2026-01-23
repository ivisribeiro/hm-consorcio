import { useState } from 'react'
import { Input, Button, Space, message } from 'antd'
import { SearchOutlined, LoadingOutlined } from '@ant-design/icons'
import { utilsApi } from '../../api/clientes'

const CEPInput = ({ value, onChange, onAddressFound, ...props }) => {
  const [loading, setLoading] = useState(false)

  const formatCEP = (val) => {
    if (!val) return ''
    const numbers = val.replace(/\D/g, '').slice(0, 8)
    if (numbers.length <= 5) return numbers
    return `${numbers.slice(0, 5)}-${numbers.slice(5)}`
  }

  const handleChange = (e) => {
    const formatted = formatCEP(e.target.value)
    onChange?.(formatted)
  }

  const handleSearch = async () => {
    const cep = value?.replace(/\D/g, '')
    if (!cep || cep.length !== 8) {
      message.error('CEP deve ter 8 dígitos')
      return
    }

    setLoading(true)
    try {
      const result = await utilsApi.buscarCEP(cep)
      message.success('Endereço encontrado!')
      onAddressFound?.(result)
    } catch (error) {
      message.error(error.response?.data?.detail || 'CEP não encontrado')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Space.Compact style={{ width: '100%' }}>
      <Input
        {...props}
        value={value}
        onChange={handleChange}
        placeholder="00000-000"
        maxLength={9}
      />
      <Button
        onClick={handleSearch}
        loading={loading}
        icon={loading ? <LoadingOutlined /> : <SearchOutlined />}
      >
        Buscar
      </Button>
    </Space.Compact>
  )
}

export default CEPInput
