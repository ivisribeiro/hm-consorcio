import { Input } from 'antd'

const PhoneInput = ({ value, onChange, ...props }) => {
  const formatPhone = (val) => {
    if (!val) return ''
    const numbers = val.replace(/\D/g, '').slice(0, 11)

    if (numbers.length <= 2) return `(${numbers}`
    if (numbers.length <= 6) return `(${numbers.slice(0, 2)}) ${numbers.slice(2)}`
    if (numbers.length <= 10) return `(${numbers.slice(0, 2)}) ${numbers.slice(2, 6)}-${numbers.slice(6)}`
    return `(${numbers.slice(0, 2)}) ${numbers.slice(2, 7)}-${numbers.slice(7)}`
  }

  const handleChange = (e) => {
    const formatted = formatPhone(e.target.value)
    onChange?.(formatted)
  }

  return (
    <Input
      {...props}
      value={value}
      onChange={handleChange}
      placeholder="(00) 00000-0000"
      maxLength={15}
    />
  )
}

export default PhoneInput
