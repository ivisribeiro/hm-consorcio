import { useState, useEffect } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { Form, Button, Card, Row, Col, Select, Table, Radio, message, Spin, Descriptions, Tag } from 'antd'
import { SaveOutlined, ArrowLeftOutlined } from '@ant-design/icons'
import { beneficiosApi, tabelasCreditoApi } from '../../api/beneficios'
import { clientesApi, unidadesApi } from '../../api/clientes'
import { representantesApi } from '../../api/representantes'
import { useAuth } from '../../contexts/AuthContext'

const tipoBemLabels = { imovel: 'Imóvel', carro: 'Carro', moto: 'Moto' }

const BeneficioForm = () => {
  const navigate = useNavigate()
  const { id } = useParams()
  const [searchParams] = useSearchParams()
  const clienteIdParam = searchParams.get('cliente_id')
  const { user } = useAuth()

  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [clientes, setClientes] = useState([])
  const [unidades, setUnidades] = useState([])
  const [representantes, setRepresentantes] = useState([])
  const [tabelas, setTabelas] = useState([])
  const [selectedCliente, setSelectedCliente] = useState(null)
  const [tipoBem, setTipoBem] = useState('imovel')
  const [selectedTabela, setSelectedTabela] = useState(null)

  const isEdit = !!id

  useEffect(() => {
    loadInitialData()
  }, [])

  useEffect(() => {
    if (tipoBem) {
      loadTabelas(tipoBem)
    }
  }, [tipoBem])

  const loadInitialData = async () => {
    setLoading(true)
    try {
      const [clientesData, unidadesData, representantesData] = await Promise.all([
        clientesApi.list({ limit: 100 }),
        unidadesApi.list(),
        representantesApi.list(),
      ])
      setClientes(clientesData)
      setUnidades(unidadesData)
      setRepresentantes(representantesData)

      if (clienteIdParam) {
        const cliente = clientesData.find(c => c.id === parseInt(clienteIdParam))
        if (cliente) {
          setSelectedCliente(cliente)
          form.setFieldValue('cliente_id', parseInt(clienteIdParam))
        }
      }
    } catch (error) {
      message.error('Erro ao carregar dados')
    } finally {
      setLoading(false)
    }
  }

  const loadTabelas = async (tipo) => {
    try {
      const data = await tabelasCreditoApi.list({ tipo_bem: tipo })
      setTabelas(data)
    } catch (error) {
      message.error('Erro ao carregar tabelas de crédito')
    }
  }

  const handleClienteChange = (clienteId) => {
    const cliente = clientes.find(c => c.id === clienteId)
    setSelectedCliente(cliente)
  }

  const handleTabelaSelect = (tabela) => {
    setSelectedTabela(tabela)
    form.setFieldValue('tabela_credito_id', tabela.id)
  }

  const onFinish = async (values) => {
    if (!selectedTabela) {
      message.error('Selecione uma tabela de crédito')
      return
    }

    setSaving(true)
    try {
      const data = {
        cliente_id: values.cliente_id,
        tabela_credito_id: selectedTabela.id,
        unidade_id: values.unidade_id || user.unidade_id,
        representante_id: values.representante_id,
      }

      await beneficiosApi.create(data)
      message.success('Benefício criado com sucesso!')
      navigate('/beneficios')
    } catch (error) {
      message.error(error.response?.data?.detail || 'Erro ao criar benefício')
    } finally {
      setSaving(false)
    }
  }

  const tabelaColumns = [
    { title: 'Nome', dataIndex: 'nome', key: 'nome' },
    { title: 'Prazo', dataIndex: 'prazo', key: 'prazo', render: (v) => `${v} meses` },
    { title: 'Valor Crédito', dataIndex: 'valor_credito', key: 'valor_credito', render: (v) => `R$ ${Number(v).toLocaleString('pt-BR')}` },
    { title: 'Parcela', dataIndex: 'parcela', key: 'parcela', render: (v) => `R$ ${Number(v).toLocaleString('pt-BR')}` },
    { title: 'Fundo Reserva', dataIndex: 'fundo_reserva', key: 'fundo_reserva', render: (v) => `${v}%` },
  ]

  if (loading) {
    return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />
  }

  return (
    <Card
      title={isEdit ? 'Editar Benefício' : 'Novo Benefício'}
      extra={<Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/beneficios')}>Voltar</Button>}
    >
      <Form form={form} layout="vertical" onFinish={onFinish}>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="cliente_id" label="Cliente" rules={[{ required: true }]}>
              <Select
                placeholder="Selecione o cliente"
                showSearch
                optionFilterProp="children"
                onChange={handleClienteChange}
              >
                {clientes.map(c => (
                  <Select.Option key={c.id} value={c.id}>{c.nome} - {c.cpf}</Select.Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="unidade_id" label="Unidade" initialValue={user?.unidade_id}>
              <Select placeholder="Selecione a unidade">
                {unidades.map(u => (<Select.Option key={u.id} value={u.id}>{u.nome}</Select.Option>))}
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="representante_id" label="Representante" rules={[{ required: true, message: 'Selecione o representante' }]}>
              <Select
                placeholder="Selecione o representante"
                showSearch
                optionFilterProp="children"
              >
                {representantes.map(r => (
                  <Select.Option key={r.id} value={r.id}>{r.nome} - {r.razao_social}</Select.Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
        </Row>

        {selectedCliente && (
          <Card size="small" style={{ marginBottom: 16, background: '#f5f5f5' }}>
            <Descriptions title="Dados do Cliente" size="small" column={4}>
              <Descriptions.Item label="Salário">
                {selectedCliente.salario ? `R$ ${Number(selectedCliente.salario).toLocaleString('pt-BR')}` : 'Não informado'}
              </Descriptions.Item>
              <Descriptions.Item label="Parcela Máx (30%)">
                {selectedCliente.salario ? `R$ ${(Number(selectedCliente.salario) * 0.3).toLocaleString('pt-BR')}` : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Cidade">{selectedCliente.cidade || '-'}</Descriptions.Item>
              <Descriptions.Item label="Telefone">{selectedCliente.telefone}</Descriptions.Item>
            </Descriptions>
          </Card>
        )}

        <Form.Item label="Tipo de Bem">
          <Radio.Group value={tipoBem} onChange={(e) => { setTipoBem(e.target.value); setSelectedTabela(null); }}>
            <Radio.Button value="imovel">Imóvel</Radio.Button>
            <Radio.Button value="carro">Carro</Radio.Button>
            <Radio.Button value="moto">Moto</Radio.Button>
          </Radio.Group>
        </Form.Item>

        <Card title="Selecione o Plano" size="small">
          <Table
            columns={tabelaColumns}
            dataSource={tabelas}
            rowKey="id"
            size="small"
            pagination={false}
            rowSelection={{
              type: 'radio',
              selectedRowKeys: selectedTabela ? [selectedTabela.id] : [],
              onChange: (_, selectedRows) => handleTabelaSelect(selectedRows[0]),
            }}
            onRow={(record) => ({ onClick: () => handleTabelaSelect(record), style: { cursor: 'pointer' } })}
          />
        </Card>

        {selectedTabela && (
          <Card title="Resumo do Benefício" size="small" style={{ marginTop: 16, background: '#e6f7ff' }}>
            <Descriptions column={3}>
              <Descriptions.Item label="Tipo">{tipoBemLabels[selectedTabela.tipo_bem]}</Descriptions.Item>
              <Descriptions.Item label="Valor do Crédito">R$ {Number(selectedTabela.valor_credito).toLocaleString('pt-BR')}</Descriptions.Item>
              <Descriptions.Item label="Parcela Mensal">R$ {Number(selectedTabela.parcela).toLocaleString('pt-BR')}</Descriptions.Item>
              <Descriptions.Item label="Prazo">{selectedTabela.prazo} meses</Descriptions.Item>
              <Descriptions.Item label="Fundo de Reserva">{selectedTabela.fundo_reserva}%</Descriptions.Item>
              <Descriptions.Item label="Taxa Administração">{selectedTabela.taxa_administracao}%</Descriptions.Item>
            </Descriptions>
          </Card>
        )}

        <div style={{ marginTop: 24, textAlign: 'right' }}>
          <Button type="primary" htmlType="submit" loading={saving} icon={<SaveOutlined />} size="large" disabled={!selectedTabela}>
            Criar Benefício
          </Button>
        </div>
      </Form>
    </Card>
  )
}

export default BeneficioForm
