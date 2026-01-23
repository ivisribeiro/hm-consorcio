import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Table, Button, Input, Select, Tag, Space, message, Popconfirm, Typography } from 'antd'
import { EyeOutlined, DeleteOutlined, FilePdfOutlined, SearchOutlined, PlusOutlined } from '@ant-design/icons'
import { contratosApi } from '../../api/contratos'

const { Title } = Typography
const { Option } = Select

const statusConfig = {
  gerado: { label: 'Gerado', color: 'blue' },
  enviado_assinatura: { label: 'Enviado p/ Assinatura', color: 'orange' },
  assinado: { label: 'Assinado', color: 'green' },
  registrado: { label: 'Registrado', color: 'cyan' },
  cancelado: { label: 'Cancelado', color: 'red' },
}

const Contratos = () => {
  const navigate = useNavigate()
  const [contratos, setContratos] = useState([])
  const [loading, setLoading] = useState(false)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState(null)

  useEffect(() => {
    loadContratos()
  }, [statusFilter])

  const loadContratos = async () => {
    setLoading(true)
    try {
      const params = {}
      if (statusFilter) params.status = statusFilter
      if (search) params.search = search
      const data = await contratosApi.list(params)
      setContratos(data)
    } catch (error) {
      message.error('Erro ao carregar contratos')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    loadContratos()
  }

  const handleDelete = async (id) => {
    try {
      await contratosApi.delete(id)
      message.success('Contrato cancelado com sucesso')
      loadContratos()
    } catch (error) {
      message.error(error.response?.data?.detail || 'Erro ao cancelar contrato')
    }
  }

  const handleDownloadPdf = async (contrato) => {
    try {
      const blob = await contratosApi.downloadPdf(contrato.id)
      contratosApi.savePdf(blob, `contrato_${contrato.numero}.pdf`)
      message.success('PDF gerado com sucesso')
    } catch (error) {
      message.error('Erro ao gerar PDF')
    }
  }

  const formatCurrency = (value) => {
    if (!value) return 'R$ 0,00'
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)
  }

  const formatDate = (dateString) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('pt-BR')
  }

  const formatCPF = (cpf) => {
    if (!cpf) return '-'
    const cleaned = cpf.replace(/\D/g, '')
    if (cleaned.length === 11) {
      return `${cleaned.slice(0,3)}.${cleaned.slice(3,6)}.${cleaned.slice(6,9)}-${cleaned.slice(9)}`
    }
    return cpf
  }

  const columns = [
    {
      title: 'Numero',
      dataIndex: 'numero',
      key: 'numero',
      width: 120,
      render: (text) => <strong>{text}</strong>,
    },
    {
      title: 'Cliente',
      key: 'cliente',
      render: (_, record) => (
        <div>
          <div>{record.cliente_nome || '-'}</div>
          <small style={{ color: '#888' }}>{formatCPF(record.cliente_cpf)}</small>
        </div>
      ),
    },
    {
      title: 'Valor do Credito',
      dataIndex: 'valor_credito',
      key: 'valor_credito',
      width: 150,
      render: (value) => formatCurrency(value),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 160,
      render: (status) => {
        const config = statusConfig[status] || { label: status, color: 'default' }
        return <Tag color={config.color}>{config.label}</Tag>
      },
    },
    {
      title: 'Data Geracao',
      dataIndex: 'data_geracao',
      key: 'data_geracao',
      width: 120,
      render: (date) => formatDate(date),
    },
    {
      title: 'Data Assinatura',
      dataIndex: 'data_assinatura',
      key: 'data_assinatura',
      width: 120,
      render: (date) => formatDate(date),
    },
    {
      title: 'Acoes',
      key: 'acoes',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            icon={<EyeOutlined />}
            size="small"
            onClick={() => navigate(`/contratos/${record.id}`)}
          />
          <Button
            icon={<FilePdfOutlined />}
            size="small"
            onClick={() => handleDownloadPdf(record)}
          />
          {record.status !== 'registrado' && record.status !== 'assinado' && (
            <Popconfirm
              title="Cancelar contrato?"
              description="Esta acao nao pode ser desfeita"
              onConfirm={() => handleDelete(record.id)}
              okText="Sim"
              cancelText="Nao"
            >
              <Button
                danger
                icon={<DeleteOutlined />}
                size="small"
              />
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={2}>Contratos</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/beneficios')}
        >
          Novo Contrato (via Beneficio)
        </Button>
      </div>

      <Card>
        <div style={{ marginBottom: 16, display: 'flex', gap: 16 }}>
          <Input
            placeholder="Buscar por nome, CPF ou numero..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onPressEnter={handleSearch}
            style={{ width: 300 }}
            suffix={<SearchOutlined onClick={handleSearch} style={{ cursor: 'pointer' }} />}
          />
          <Select
            placeholder="Filtrar por status"
            value={statusFilter}
            onChange={setStatusFilter}
            allowClear
            style={{ width: 200 }}
          >
            {Object.entries(statusConfig).map(([key, config]) => (
              <Option key={key} value={key}>{config.label}</Option>
            ))}
          </Select>
        </div>

        <Table
          columns={columns}
          dataSource={contratos}
          rowKey="id"
          loading={loading}
          pagination={{
            defaultPageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `Total: ${total} contratos`,
          }}
        />
      </Card>
    </div>
  )
}

export default Contratos
