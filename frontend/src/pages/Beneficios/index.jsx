import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Table, Button, Card, Tag, Space, Select, message } from 'antd'
import { PlusOutlined, EyeOutlined } from '@ant-design/icons'
import { beneficiosApi } from '../../api/beneficios'

const statusColors = {
  rascunho: 'default',
  proposto: 'processing',
  aceito: 'success',
  rejeitado: 'error',
  contrato_gerado: 'cyan',
  contrato_assinado: 'blue',
  aguardando_cadastro: 'orange',
  cadastrado: 'purple',
  termo_gerado: 'geekblue',
  ativo: 'green',
  cancelado: 'red',
}

const statusLabels = {
  rascunho: 'Rascunho',
  proposto: 'Proposto',
  aceito: 'Aceito',
  rejeitado: 'Rejeitado',
  contrato_gerado: 'Contrato Gerado',
  contrato_assinado: 'Contrato Assinado',
  aguardando_cadastro: 'Aguardando Cadastro',
  cadastrado: 'Cadastrado',
  termo_gerado: 'Termo Gerado',
  ativo: 'Ativo',
  cancelado: 'Cancelado',
}

const tipoBemLabels = {
  imovel: 'Imóvel',
  carro: 'Carro',
  moto: 'Moto',
}

const BeneficiosList = () => {
  const navigate = useNavigate()
  const [beneficios, setBeneficios] = useState([])
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({ status: null, tipo_bem: null })

  const fetchBeneficios = async () => {
    setLoading(true)
    try {
      const data = await beneficiosApi.list(filters)
      setBeneficios(data)
    } catch (error) {
      message.error('Erro ao carregar benefícios')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchBeneficios()
  }, [filters])

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
    { title: 'Cliente', dataIndex: 'cliente_nome', key: 'cliente_nome' },
    { title: 'Tipo', dataIndex: 'tipo_bem', key: 'tipo_bem', render: (val) => tipoBemLabels[val] || val },
    { title: 'Valor Crédito', dataIndex: 'valor_credito', key: 'valor_credito', render: (val) => `R$ ${Number(val).toLocaleString('pt-BR')}` },
    { title: 'Parcela', dataIndex: 'parcela', key: 'parcela', render: (val) => `R$ ${Number(val).toLocaleString('pt-BR')}` },
    { title: 'Prazo', dataIndex: 'prazo_grupo', key: 'prazo_grupo', render: (val) => `${val} meses` },
    { title: 'Grupo/Cota', key: 'grupo_cota', render: (_, record) => record.grupo ? `${record.grupo}/${record.cota}` : '-' },
    { title: 'Status', dataIndex: 'status', key: 'status', render: (status) => <Tag color={statusColors[status]}>{statusLabels[status] || status}</Tag> },
    {
      title: 'Ações', key: 'actions',
      render: (_, record) => (
        <Button type="link" icon={<EyeOutlined />} onClick={() => navigate(`/beneficios/${record.id}`)} />
      ),
    },
  ]

  return (
    <Card
      title="Benefícios"
      extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/beneficios/novo')}>Novo Benefício</Button>}
    >
      <Space style={{ marginBottom: 16 }}>
        <Select placeholder="Filtrar por Status" allowClear style={{ width: 200 }} onChange={(val) => setFilters(prev => ({ ...prev, status: val }))}>
          {Object.entries(statusLabels).map(([key, label]) => (<Select.Option key={key} value={key}>{label}</Select.Option>))}
        </Select>
        <Select placeholder="Filtrar por Tipo" allowClear style={{ width: 150 }} onChange={(val) => setFilters(prev => ({ ...prev, tipo_bem: val }))}>
          {Object.entries(tipoBemLabels).map(([key, label]) => (<Select.Option key={key} value={key}>{label}</Select.Option>))}
        </Select>
      </Space>
      <Table columns={columns} dataSource={beneficios} rowKey="id" loading={loading} />
    </Card>
  )
}

export default BeneficiosList
