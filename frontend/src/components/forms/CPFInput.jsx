import { useState } from 'react'
import { Input, Button, Space, message } from 'antd'
import { CheckCircleOutlined, LoadingOutlined } from '@ant-design/icons'
import { utilsApi } from '../../api/clientes'

const CPFInput = ({ value, onChange, onValidate, ...props }) => {
  const [loading, setLoading] = useState(false)
  const [validated, setValidated] = useState(false)

  const formatCPF = (val) => {
    if (!val) return ''
    const numbers = val.replace(/\D/g, '').slice(0, 11)
    if (numbers.length <= 3) return numbers
    if (numbers.length <= 6) return `${numbers.slice(0, 3)}.${numbers.slice(3)}`
    if (numbers.length <= 9) return `${numbers.slice(0, 3)}.${numbers.slice(3, 6)}.${numbers.slice(6)}`
    return `${numbers.slice(0, 3)}.${numbers.slice(3, 6)}.${numbers.slice(6, 9)}-${numbers.slice(9)}`
  }

  const handleChange = (e) => {
    const formatted = formatCPF(e.target.value)
    setValidated(false)
    onChange?.(formatted)
  }

  const handleValidate = async () => {
    if (!value || value.replace(/\D/g, '').length !== 11) {
      message.error('CPF deve ter 11 dígitos')
      return
    }

    setLoading(true)
    try {
      const result = await utilsApi.validarCPF(value)
      setValidated(true)
      message.success('CPF válido!')
      onValidate?.(result)
    } catch (error) {
      message.error(error.response?.data?.detail || 'CPF inválido')
      setValidated(false)
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
        placeholder="000.000.000-00"
        maxLength={14}
        suffix={validated ? <CheckCircleOutlined style={{ color: '#52c41a' }} /> : null}
      />
      <Button
        onClick={handleValidate}
        loading={loading}
        icon={loading ? <LoadingOutlined /> : null}
      >
        Validar
      </Button>
    </Space.Compact>
  )
}

export default CPFInput
