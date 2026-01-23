import { useState, useEffect } from 'react'
import { Table, Button, Space, Card, Tag, message, Modal, Form, Input, Select, InputNumber } from 'antd'
import { PlusOutlined, EditOutlined } from '@ant-design/icons'
import { tabelasCreditoApi } from '../../api/beneficios'

const tipoBemOptions = [
  { value: 'imovel', label: 'Imóvel' },
  { value: 'carro', label: 'Carro' },
  { value: 'moto', label: 'Moto' },
]

const tipoBemColors = {
  imovel: 'blue',
  carro: 'green',
  moto: 'orange',
}

const TabelasCreditoList = () => {
  const [tabelas, setTabelas] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingTabela, setEditingTabela] = useState(null)
  const [filterTipo, setFilterTipo] = useState(null)
  const [form] = Form.useForm()

  const fetchTabelas = async () => {
    setLoading(true)
    try {
      const params = filterTipo ? { tipo_bem: filterTipo } : {}
      const data = await tabelasCreditoApi.list(params)
      setTabelas(data)
    } catch (error) {
      message.error('Erro ao carregar tabelas de crédito')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTabelas()
  }, [filterTipo])

  const handleOpenModal = (tabela = null) => {
    setEditingTabela(tabela)
    if (tabela) {
      form.setFieldsValue({
        ...tabela,
        valor_credito: parseFloat(tabela.valor_credito),
        parcela: parseFloat(tabela.parcela),
        fundo_reserva: parseFloat(tabela.fundo_reserva),
        taxa_administracao: parseFloat(tabela.taxa_administracao),
        seguro_prestamista: parseFloat(tabela.seguro_prestamista),
      })
    } else {
      form.resetFields()
      form.setFieldsValue({
        fundo_reserva: 2.5,
        taxa_administracao: 26.0,
        seguro_prestamista: 0,
        indice_correcao: 'INCC',
        qtd_participantes: 4076,
        tipo_plano: 'Normal',
      })
    }
    setModalOpen(true)
  }

  const handleCloseModal = () => {
    setModalOpen(false)
    setEditingTabela(null)
    form.resetFields()
  }

  const handleSubmit = async (values) => {
    try {
      if (editingTabela) {
        await tabelasCreditoApi.update(editingTabela.id, values)
        message.success('Tabela atualizada com sucesso')
      } else {
        await tabelasCreditoApi.create(values)
        message.success('Tabela criada com sucesso')
      }
      handleCloseModal()
      fetchTabelas()
    } catch (error) {
      message.error(error.response?.data?.detail || 'Erro ao salvar tabela')
    }
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value)
  }

  const columns = [
    {
      title: 'Nome',
      dataIndex: 'nome',
      key: 'nome',
      sorter: (a, b) => a.nome.localeCompare(b.nome),
    },
    {
      title: 'Tipo',
      dataIndex: 'tipo_bem',
      key: 'tipo_bem',
      render: (tipo) => (
        <Tag color={tipoBemColors[tipo]}>
          {tipoBemOptions.find(t => t.value === tipo)?.label || tipo}
        </Tag>
      ),
    },
    {
      title: 'Crédito',
      dataIndex: 'valor_credito',
      key: 'valor_credito',
      render: (val) => formatCurrency(val),
      sorter: (a, b) => parseFloat(a.valor_credito) - parseFloat(b.valor_credito),
    },
    {
      title: 'Parcela',
      dataIndex: 'parcela',
      key: 'parcela',
      render: (val) => formatCurrency(val),
    },
    {
      title: 'Prazo',
      dataIndex: 'prazo',
      key: 'prazo',
      render: (val) => `${val} meses`,
    },
    {
      title: 'Fundo Reserva',
      dataIndex: 'fundo_reserva',
      key: 'fundo_reserva',
      render: (val) => `${val}%`,
    },
    {
      title: 'Taxa Admin.',
      dataIndex: 'taxa_administracao',
      key: 'taxa_administracao',
      render: (val) => `${val}%`,
    },
    {
      title: 'Status',
      dataIndex: 'ativo',
      key: 'ativo',
      render: (ativo) => (
        <Tag color={ativo ? 'green' : 'red'}>
          {ativo ? 'Ativa' : 'Inativa'}
        </Tag>
      ),
    },
    {
      title: 'Ações',
      key: 'actions',
      width: 80,
      render: (_, record) => (
        <Button
          type="link"
          icon={<EditOutlined />}
          onClick={() => handleOpenModal(record)}
        />
      ),
    },
  ]

  return (
    <div>
      <Card
        title="Tabelas de Crédito"
        extra={
          <Space>
            <Select
              placeholder="Filtrar por tipo"
              allowClear
              style={{ width: 150 }}
              options={tipoBemOptions}
              onChange={setFilterTipo}
              value={filterTipo}
            />
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => handleOpenModal()}
            >
              Nova Tabela
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={tabelas}
          rowKey="id"
          loading={loading}
        />
      </Card>

      <Modal
        title={editingTabela ? 'Editar Tabela de Crédito' : 'Nova Tabela de Crédito'}
        open={modalOpen}
        onCancel={handleCloseModal}
        footer={null}
        width={700}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="nome"
            label="Nome da Tabela"
            rules={[{ required: true, message: 'Informe o nome' }]}
          >
            <Input placeholder="Ex: Imóvel 100K - 120m" />
          </Form.Item>

          <Space style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="tipo_bem"
              label="Tipo de Bem"
              rules={[{ required: true, message: 'Selecione o tipo' }]}
              style={{ width: 150 }}
            >
              <Select options={tipoBemOptions} />
            </Form.Item>

            <Form.Item
              name="valor_credito"
              label="Valor do Crédito (R$)"
              rules={[{ required: true, message: 'Informe o valor' }]}
              style={{ flex: 1 }}
            >
              <InputNumber
                style={{ width: '100%' }}
                formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, '.')}
                parser={value => value.replace(/\./g, '')}
              />
            </Form.Item>

            <Form.Item
              name="parcela"
              label="Parcela (R$)"
              rules={[{ required: true, message: 'Informe a parcela' }]}
              style={{ flex: 1 }}
            >
              <InputNumber
                style={{ width: '100%' }}
                formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, '.')}
                parser={value => value.replace(/\./g, '')}
              />
            </Form.Item>
          </Space>

          <Space style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="prazo"
              label="Prazo (meses)"
              rules={[{ required: true, message: 'Informe o prazo' }]}
              style={{ width: 120 }}
            >
              <InputNumber style={{ width: '100%' }} min={1} />
            </Form.Item>

            <Form.Item
              name="fundo_reserva"
              label="Fundo Reserva (%)"
              rules={[{ required: true, message: 'Informe o fundo' }]}
              style={{ width: 150 }}
            >
              <InputNumber style={{ width: '100%' }} min={0} step={0.1} />
            </Form.Item>

            <Form.Item
              name="taxa_administracao"
              label="Taxa Admin. (%)"
              style={{ width: 150 }}
            >
              <InputNumber style={{ width: '100%' }} min={0} step={0.1} />
            </Form.Item>

            <Form.Item
              name="seguro_prestamista"
              label="Seguro (%)"
              style={{ width: 120 }}
            >
              <InputNumber style={{ width: '100%' }} min={0} step={0.1} />
            </Form.Item>
          </Space>

          <Space style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="indice_correcao"
              label="Índice Correção"
              style={{ width: 150 }}
            >
              <Select
                options={[
                  { value: 'INCC', label: 'INCC' },
                  { value: 'IPCA', label: 'IPCA' },
                  { value: 'IGP-M', label: 'IGP-M' },
                ]}
              />
            </Form.Item>

            <Form.Item
              name="qtd_participantes"
              label="Qtd. Participantes"
              style={{ width: 150 }}
            >
              <InputNumber style={{ width: '100%' }} min={1} />
            </Form.Item>

            <Form.Item
              name="tipo_plano"
              label="Tipo de Plano"
              style={{ flex: 1 }}
            >
              <Input />
            </Form.Item>
          </Space>

          {editingTabela && (
            <Form.Item
              name="ativo"
              label="Status"
            >
              <Select
                options={[
                  { value: true, label: 'Ativa' },
                  { value: false, label: 'Inativa' },
                ]}
              />
            </Form.Item>
          )}

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                Salvar
              </Button>
              <Button onClick={handleCloseModal}>
                Cancelar
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default TabelasCreditoList
