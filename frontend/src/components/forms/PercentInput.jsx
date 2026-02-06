import { InputNumber } from 'antd'

const PercentInput = ({ value, onChange, ...props }) => {
  return (
    <InputNumber
      {...props}
      value={value}
      onChange={onChange}
      style={{ width: '100%' }}
      min={0}
      max={100}
      step={0.01}
      precision={2}
      decimalSeparator=","
      formatter={val => {
        const num = parseFloat(val) || 0
        return `${num.toFixed(2).replace('.', ',')}%`
      }}
      parser={val => val.replace(/%/g, '').replace(',', '.')}
    />
  )
}

export default PercentInput
