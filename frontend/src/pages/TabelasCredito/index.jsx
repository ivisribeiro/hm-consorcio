import { useState, useEffect } from 'react'
import { Table, Button, Space, Card, Tag, message, Modal, Form, Input, Select, InputNumber, Upload, Alert, Typography } from 'antd'
import { PlusOutlined, EditOutlined, UploadOutlined, DownloadOutlined } from '@ant-design/icons'
import { tabelasCreditoApi, administradorasApi } from '../../api/beneficios'
import { getErrorMessage } from '../../utils/errorHandler'

const { Text } = Typography

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
  const [administradoras, setAdministradoras] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [importModalOpen, setImportModalOpen] = useState(false)
  const [editingTabela, setEditingTabela] = useState(null)
  const [filterTipo, setFilterTipo] = useState(null)
  const [filterAdmin, setFilterAdmin] = useState(null)
  const [importResult, setImportResult] = useState(null)
  const [importing, setImporting] = useState(false)
  const [form] = Form.useForm()
  const [importForm] = Form.useForm()

  const fetchTabelas = async () => {
    setLoading(true)
    try {
      const params = {}
      if (filterTipo) params.tipo_bem = filterTipo
      if (filterAdmin) params.administradora_id = filterAdmin
      const data = await tabelasCreditoApi.list(params)
      setTabelas(data)
    } catch (error) {
      message.error('Erro ao carregar tabelas de crédito')
    } finally {
      setLoading(false)
    }
  }

  const fetchAdministradoras = async () => {
    try {
      const data = await administradorasApi.list()
      setAdministradoras(data)
    } catch (error) {
      console.error('Erro ao carregar administradoras:', error)
    }
  }

  useEffect(() => {
    fetchTabelas()
    fetchAdministradoras()
  }, [filterTipo, filterAdmin])

  const handleOpenModal = (tabela = null) => {
    setEditingTabela(tabela)
    if (tabela) {
      form.setFieldsValue({
        ...tabela,
        valor_credito: parseFloat(tabela.valor_credito),
        parcela: parseFloat(tabela.parcela),
        valor_intermediacao: tabela.valor_intermediacao ? parseFloat(tabela.valor_intermediacao) : 0,
        fundo_reserva: parseFloat(tabela.fundo_reserva),
        taxa_administracao: parseFloat(tabela.taxa_administracao),
        seguro_prestamista: parseFloat(tabela.seguro_prestamista),
        administradora_id: tabela.administradora_id || tabela.administradora?.id,
      })
    } else {
      form.resetFields()
      form.setFieldsValue({
        fundo_reserva: 2.5,
        taxa_administracao: 26.0,
        seguro_prestamista: 0,
        valor_intermediacao: 0,
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
      message.error(getErrorMessage(error, 'Erro ao salvar tabela'))
    }
  }

  const handleImport = async () => {
    try {
      const values = await importForm.validateFields()
      const file = values.file?.fileList?.[0]?.originFileObj

      if (!file) {
        message.error('Selecione um arquivo CSV')
        return
      }

      setImporting(true)
      setImportResult(null)

      const result = await tabelasCreditoApi.importarCSV(file, values.administradora_id)
      setImportResult(result)

      if (result.importados > 0) {
        message.success(`${result.importados} tabelas importadas com sucesso`)
        fetchTabelas()
      }
    } catch (error) {
      message.error(getErrorMessage(error, 'Erro ao importar CSV'))
    } finally {
      setImporting(false)
    }
  }

  const handleCloseImportModal = () => {
    setImportModalOpen(false)
    setImportResult(null)
    importForm.resetFields()
  }

  const downloadTemplate = () => {
    const template = 'nome;tipo_bem;prazo;valor_credito;parcela;valor_intermediacao;fundo_reserva;taxa_administracao;seguro_prestamista;indice_correcao;qtd_participantes;tipo_plano\n' +
      'Imóvel 100K 120m;imovel;120;100000;850.00;500;2.5;26.0;0;INCC;4076;Normal\n' +
      'Carro 50K 80m;carro;80;50000;650.00;300;2.5;26.0;0;INCC;4076;Normal'

    const blob = new Blob([template], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = 'modelo_tabelas_credito.csv'
    link.click()
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
      title: 'Administradora',
      key: 'administradora',
      render: (_, record) => record.administradora?.nome || '-',
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
      title: 'Intermediação',
      dataIndex: 'valor_intermediacao',
      key: 'valor_intermediacao',
      render: (val) => val ? formatCurrency(val) : '-',
    },
    {
      title: 'Prazo',
      dataIndex: 'prazo',
      key: 'prazo',
      render: (val) => `${val} meses`,
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
              placeholder="Administradora"
              allowClear
              style={{ width: 180 }}
              options={administradoras.map(a => ({ value: a.id, label: a.nome }))}
              onChange={setFilterAdmin}
              value={filterAdmin}
            />
            <Select
              placeholder="Tipo de bem"
              allowClear
              style={{ width: 130 }}
              options={tipoBemOptions}
              onChange={setFilterTipo}
              value={filterTipo}
            />
            <Button
              icon={<UploadOutlined />}
              onClick={() => setImportModalOpen(true)}
            >
              Importar CSV
            </Button>
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
          pagination={{
            defaultPageSize: 20,
            showSizeChanger: true,
            showTotal: (total) => `Total: ${total} tabelas`
          }}
        />
      </Card>

      {/* Modal de Edição/Criação */}
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

          <Form.Item
            name="administradora_id"
            label="Administradora"
          >
            <Select
              placeholder="Selecione a administradora"
              allowClear
              options={administradoras.map(a => ({ value: a.id, label: a.nome }))}
            />
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
                precision={2}
                decimalSeparator=","
                formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, '.').replace('.,', ',')}
                parser={value => value.replace(/\./g, '').replace(',', '.')}
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
                precision={2}
                decimalSeparator=","
                formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, '.').replace('.,', ',')}
                parser={value => value.replace(/\./g, '').replace(',', '.')}
              />
            </Form.Item>

            <Form.Item
              name="valor_intermediacao"
              label="Intermediação (R$)"
              style={{ flex: 1 }}
            >
              <InputNumber
                style={{ width: '100%' }}
                min={0}
                precision={2}
                decimalSeparator=","
                formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, '.').replace('.,', ',')}
                parser={value => value.replace(/\./g, '').replace(',', '.')}
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

      {/* Modal de Importação CSV */}
      <Modal
        title="Importar Tabelas via CSV"
        open={importModalOpen}
        onCancel={handleCloseImportModal}
        footer={null}
        width={600}
      >
        <Form form={importForm} layout="vertical">
          <Alert
            message="Formato do CSV"
            description={
              <div>
                <p>Colunas: nome, tipo_bem, prazo, valor_credito, parcela</p>
                <p>Opcionais: valor_intermediacao, fundo_reserva, taxa_administracao, seguro_prestamista, indice_correcao, qtd_participantes, tipo_plano</p>
                <p>Separador: vírgula (,) ou ponto-e-vírgula (;)</p>
              </div>
            }
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />

          <Form.Item
            name="administradora_id"
            label="Administradora (aplicar a todas as tabelas)"
          >
            <Select
              placeholder="Selecione a administradora"
              allowClear
              options={administradoras.map(a => ({ value: a.id, label: a.nome }))}
            />
          </Form.Item>

          <Form.Item
            name="file"
            label="Arquivo CSV"
            rules={[{ required: true, message: 'Selecione um arquivo' }]}
          >
            <Upload
              accept=".csv"
              maxCount={1}
              beforeUpload={() => false}
            >
              <Button icon={<UploadOutlined />}>Selecionar arquivo CSV</Button>
            </Upload>
          </Form.Item>

          <Button
            icon={<DownloadOutlined />}
            onClick={downloadTemplate}
            style={{ marginBottom: 16 }}
          >
            Baixar modelo CSV
          </Button>

          {importResult && (
            <Alert
              message={`Resultado: ${importResult.importados} de ${importResult.total} importadas`}
              description={
                importResult.erros.length > 0 && (
                  <div style={{ maxHeight: 150, overflow: 'auto' }}>
                    {importResult.erros.map((erro, i) => (
                      <Text key={i} type="danger" style={{ display: 'block' }}>{erro}</Text>
                    ))}
                  </div>
                )
              }
              type={importResult.erros.length > 0 ? 'warning' : 'success'}
              showIcon
              style={{ marginBottom: 16 }}
            />
          )}

          <Form.Item>
            <Space>
              <Button type="primary" onClick={handleImport} loading={importing}>
                Importar
              </Button>
              <Button onClick={handleCloseImportModal}>
                Fechar
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default TabelasCreditoList
