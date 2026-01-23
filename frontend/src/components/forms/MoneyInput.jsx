import { InputNumber } from 'antd'

const MoneyInput = ({ value, onChange, ...props }) => {
  return (
    <InputNumber
      {...props}
      value={value}
      onChange={onChange}
      formatter={(value) => `R$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, '.')}
      parser={(value) => value.replace(/R\$\s?|(\.)/g, '').replace(',', '.')}
      style={{ width: '100%' }}
      decimalSeparator=","
      precision={2}
      min={0}
    />
  )
}

export default MoneyInput
