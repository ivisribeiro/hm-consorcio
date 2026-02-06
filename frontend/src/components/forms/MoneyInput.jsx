import { InputNumber } from 'antd'

const MoneyInput = ({ value, onChange, ...props }) => {
  return (
    <InputNumber
      {...props}
      value={value}
      onChange={onChange}
      style={{ width: '100%' }}
      min={0}
      step={0.01}
      precision={2}
      decimalSeparator=","
      formatter={val => {
        if (val === null || val === undefined || val === '') return 'R$ 0,00'
        const num = parseFloat(val) || 0
        return `R$ ${num.toFixed(2).replace('.', ',').replace(/\B(?=(\d{3})+(?!\d))/g, '.')}`
      }}
      parser={val => {
        if (!val) return 0
        const cleaned = val.replace(/R\$\s?/g, '').replace(/\./g, '').replace(',', '.')
        return parseFloat(cleaned) || 0
      }}
    />
  )
}

export default MoneyInput
