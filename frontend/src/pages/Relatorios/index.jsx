import { useState, useEffect } from 'react'
import { Card, Select, Button, message, Row, Col, Typography, Descriptions, Empty, Tag, Divider, Space } from 'antd'
import { FilePdfOutlined, UserOutlined, FileTextOutlined, SolutionOutlined } from '@ant-design/icons'
import { clientesApi } from '../../api/clientes'
import { beneficiosApi } from '../../api/beneficios'
import { relatoriosApi } from '../../api/relatorios'

const { Title, Text } = Typography
const { Option } = Select

const Relatorios = () => {
  const [clientes, setClientes] = useState([])
  const [beneficios, setBeneficios] = useState([])
  const [loading, setLoading] = useState(false)
  const [loadingBeneficios, setLoadingBeneficios] = useState(false)

  // Ficha de Atendimento
  const [selectedClienteIdFicha, setSelectedClienteIdFicha] = useState(null)
  const [selectedClienteFicha, setSelectedClienteFicha] = useState(null)
  const [downloadingPdf, setDownloadingPdf] = useState(false)

  // Contrato e Termo (compartilhado)
  const [selectedClienteId, setSelectedClienteId] = useState(null)
  const [selectedCliente, setSelectedCliente] = useState(null)
  const [beneficiosFiltrados, setBeneficiosFiltrados] = useState([])
  const [selectedBeneficioId, setSelectedBeneficioId] = useState(null)
  const [selectedBeneficio, setSelectedBeneficio] = useState(null)
  const [downloadingContrato, setDownloadingContrato] = useState(false)
  const [downloadingTermo, setDownloadingTermo] = useState(false)

  useEffect(() => {
    loadClientes()
    loadBeneficios()
  }, [])

  const loadClientes = async () => {
    setLoading(true)
    try {
      const data = await clientesApi.list()
      setClientes(data)
    } catch (error) {
      message.error('Erro ao carregar clientes')
    } finally {
      setLoading(false)
    }
  }

  const loadBeneficios = async () => {
    setLoadingBeneficios(true)
    try {
      const data = await beneficiosApi.list()
      setBeneficios(data)
    } catch (error) {
      message.error('Erro ao carregar benefícios')
    } finally {
      setLoadingBeneficios(false)
    }
  }

  // Ficha de Atendimento - handlers
  const handleClienteChangeFicha = async (clienteId) => {
    setSelectedClienteIdFicha(clienteId)
    if (clienteId) {
      try {
        const data = await clientesApi.get(clienteId)
        setSelectedClienteFicha(data)
      } catch (error) {
        message.error('Erro ao carregar dados do cliente')
        setSelectedClienteFicha(null)
      }
    } else {
      setSelectedClienteFicha(null)
    }
  }

  // Contrato/Termo - handlers
  const handleClienteChange = async (clienteId) => {
    setSelectedClienteId(clienteId)
    setSelectedBeneficioId(null)
    setSelectedBeneficio(null)

    if (clienteId) {
      try {
        const data = await clientesApi.get(clienteId)
        setSelectedCliente(data)

        // Filtra benefícios desse cliente
        const beneficiosCliente = beneficios.filter(b => b.cliente_id === clienteId)
        setBeneficiosFiltrados(beneficiosCliente)
      } catch (error) {
        message.error('Erro ao carregar dados do cliente')
        setSelectedCliente(null)
        setBeneficiosFiltrados([])
      }
    } else {
      setSelectedCliente(null)
      setBeneficiosFiltrados([])
    }
  }

  const handleBeneficioChange = async (beneficioId) => {
    setSelectedBeneficioId(beneficioId)
    if (beneficioId) {
      try {
        const data = await beneficiosApi.get(beneficioId)
        setSelectedBeneficio(data)
      } catch (error) {
        message.error('Erro ao carregar dados do benefício')
        setSelectedBeneficio(null)
      }
    } else {
      setSelectedBeneficio(null)
    }
  }

  const handleDownloadFichaAtendimento = async () => {
    if (!selectedClienteIdFicha) {
      message.warning('Selecione um cliente primeiro')
      return
    }

    setDownloadingPdf(true)
    try {
      const blob = await relatoriosApi.gerarFichaAtendimento(selectedClienteIdFicha)
      const clienteNome = selectedClienteFicha?.nome || 'cliente'
      relatoriosApi.downloadPdf(blob, `ficha_atendimento_${clienteNome.replace(/\s+/g, '_')}.pdf`)
      message.success('Ficha de Atendimento gerada com sucesso!')
    } catch (error) {
      message.error('Erro ao gerar PDF')
    } finally {
      setDownloadingPdf(false)
    }
  }

  const handleDownloadContrato = async () => {
    if (!selectedBeneficioId) {
      message.warning('Selecione um benefício primeiro')
      return
    }

    setDownloadingContrato(true)
    try {
      const blob = await relatoriosApi.gerarContratoPdf(selectedBeneficioId)
      const clienteNome = selectedCliente?.nome || 'cliente'
      relatoriosApi.downloadPdf(blob, `contrato_${clienteNome.replace(/\s+/g, '_')}.pdf`)
      message.success('Contrato gerado com sucesso!')
    } catch (error) {
      console.error('Erro ao gerar contrato:', error)
      message.error('Erro ao gerar contrato')
    } finally {
      setDownloadingContrato(false)
    }
  }

  const handleDownloadTermo = async () => {
    if (!selectedBeneficioId) {
      message.warning('Selecione um benefício primeiro')
      return
    }

    setDownloadingTermo(true)
    try {
      const blob = await relatoriosApi.gerarTermoAdesaoPdf(selectedBeneficioId)
      const clienteNome = selectedCliente?.nome || 'cliente'
      relatoriosApi.downloadPdf(blob, `termo_adesao_${clienteNome.replace(/\s+/g, '_')}.pdf`)
      message.success('Termo de Adesão gerado com sucesso!')
    } catch (error) {
      console.error('Erro ao gerar termo:', error)
      message.error('Erro ao gerar termo de adesão')
    } finally {
      setDownloadingTermo(false)
    }
  }

  const formatCPF = (cpf) => {
    if (!cpf) return '-'
    const cleaned = cpf.replace(/\D/g, '')
    if (cleaned.length === 11) {
      return `${cleaned.slice(0,3)}.${cleaned.slice(3,6)}.${cleaned.slice(6,9)}-${cleaned.slice(9)}`
    }
    return cpf
  }

  const formatPhone = (phone) => {
    if (!phone) return '-'
    return phone
  }

  const formatDate = (dateString) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('pt-BR')
  }

  const formatCurrency = (value) => {
    if (!value) return 'R$ 0,00'
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)
  }

  const tipoBemLabels = {
    imovel: 'Imóvel',
    carro: 'Carro',
    moto: 'Moto'
  }

  const statusLabels = {
    rascunho: { text: 'Rascunho', color: 'default' },
    em_analise: { text: 'Em Análise', color: 'processing' },
    ativo: { text: 'Ativo', color: 'success' },
    contemplado: { text: 'Contemplado', color: 'gold' },
    cancelado: { text: 'Cancelado', color: 'error' },
    finalizado: { text: 'Finalizado', color: 'default' }
  }

  return (
    <div>
      <Title level={2}>Relatórios</Title>

      {/* Ficha de Atendimento */}
      <Card title="Ficha de Atendimento" style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} md={16}>
            <Text strong>Selecione o Cliente:</Text>
            <Select
              showSearch
              placeholder="Buscar cliente por nome ou CPF"
              style={{ width: '100%', marginTop: 8 }}
              onChange={handleClienteChangeFicha}
              value={selectedClienteIdFicha}
              loading={loading}
              allowClear
              filterOption={(input, option) =>
                option.children.toLowerCase().includes(input.toLowerCase())
              }
              size="large"
            >
              {clientes.map(cliente => (
                <Option key={cliente.id} value={cliente.id}>
                  {cliente.nome} - {formatCPF(cliente.cpf)}
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} md={8}>
            <div style={{ display: 'flex', alignItems: 'flex-end', height: '100%' }}>
              <Button
                type="primary"
                icon={<FilePdfOutlined />}
                onClick={handleDownloadFichaAtendimento}
                loading={downloadingPdf}
                disabled={!selectedClienteIdFicha}
                size="large"
                style={{ width: '100%', marginTop: 8 }}
              >
                Gerar Ficha de Atendimento
              </Button>
            </div>
          </Col>
        </Row>

        {selectedClienteFicha ? (
          <Card
            type="inner"
            title={
              <span>
                <UserOutlined style={{ marginRight: 8 }} />
                Dados do Cliente Selecionado
              </span>
            }
            style={{ marginTop: 24 }}
          >
            <Descriptions column={{ xs: 1, sm: 2, md: 3 }} size="small">
              <Descriptions.Item label="Nome">{selectedClienteFicha.nome}</Descriptions.Item>
              <Descriptions.Item label="CPF">{formatCPF(selectedClienteFicha.cpf)}</Descriptions.Item>
              <Descriptions.Item label="Telefone">{formatPhone(selectedClienteFicha.telefone)}</Descriptions.Item>
              <Descriptions.Item label="Email">{selectedClienteFicha.email || '-'}</Descriptions.Item>
              <Descriptions.Item label="Data Nascimento">{formatDate(selectedClienteFicha.data_nascimento)}</Descriptions.Item>
              <Descriptions.Item label="Estado Civil">{selectedClienteFicha.estado_civil || '-'}</Descriptions.Item>
            </Descriptions>
          </Card>
        ) : (
          <div style={{ marginTop: 24, textAlign: 'center', padding: 40 }}>
            <Empty
              description="Selecione um cliente para visualizar os dados e gerar a ficha de atendimento"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
          </div>
        )}
      </Card>

      {/* Contrato e Termo de Adesão */}
      <Card title="Contrato e Termo de Adesão" style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} md={12}>
            <Text strong>1. Selecione o Cliente:</Text>
            <Select
              showSearch
              placeholder="Buscar cliente por nome ou CPF"
              style={{ width: '100%', marginTop: 8 }}
              onChange={handleClienteChange}
              value={selectedClienteId}
              loading={loading}
              allowClear
              filterOption={(input, option) =>
                option.children.toLowerCase().includes(input.toLowerCase())
              }
              size="large"
            >
              {clientes.map(cliente => (
                <Option key={cliente.id} value={cliente.id}>
                  {cliente.nome} - {formatCPF(cliente.cpf)}
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} md={12}>
            <Text strong>2. Selecione o Benefício:</Text>
            <Select
              showSearch
              placeholder={selectedClienteId ? "Selecione o benefício" : "Selecione um cliente primeiro"}
              style={{ width: '100%', marginTop: 8 }}
              onChange={handleBeneficioChange}
              value={selectedBeneficioId}
              loading={loadingBeneficios}
              allowClear
              disabled={!selectedClienteId}
              filterOption={(input, option) =>
                option.children.toLowerCase().includes(input.toLowerCase())
              }
              size="large"
            >
              {beneficiosFiltrados.map(beneficio => (
                <Option key={beneficio.id} value={beneficio.id}>
                  {tipoBemLabels[beneficio.tipo_bem] || beneficio.tipo_bem} - {formatCurrency(beneficio.valor_credito)} - {beneficio.grupo || 'Sem grupo'}
                </Option>
              ))}
            </Select>
          </Col>
        </Row>

        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24}>
            <Space wrap>
              <Button
                type="primary"
                icon={<FileTextOutlined />}
                onClick={handleDownloadContrato}
                loading={downloadingContrato}
                disabled={!selectedBeneficioId}
                size="large"
                style={{ backgroundColor: '#2E7D32', borderColor: '#2E7D32' }}
              >
                Gerar Contrato (10 páginas)
              </Button>
              <Button
                type="primary"
                icon={<SolutionOutlined />}
                onClick={handleDownloadTermo}
                loading={downloadingTermo}
                disabled={!selectedBeneficioId}
                size="large"
                style={{ backgroundColor: '#1565C0', borderColor: '#1565C0' }}
              >
                Gerar Termo de Adesão (3 páginas)
              </Button>
            </Space>
          </Col>
        </Row>

        {selectedBeneficio ? (
          <Card
            type="inner"
            title={
              <span>
                <FileTextOutlined style={{ marginRight: 8 }} />
                Dados do Benefício Selecionado
              </span>
            }
            style={{ marginTop: 24 }}
          >
            <Divider orientation="left" style={{ margin: '0 0 16px 0' }}>Cliente</Divider>
            <Descriptions column={{ xs: 1, sm: 2, md: 3 }} size="small">
              <Descriptions.Item label="Nome">{selectedCliente?.nome || '-'}</Descriptions.Item>
              <Descriptions.Item label="CPF">{formatCPF(selectedCliente?.cpf)}</Descriptions.Item>
              <Descriptions.Item label="Telefone">{formatPhone(selectedCliente?.telefone)}</Descriptions.Item>
            </Descriptions>

            <Divider orientation="left" style={{ margin: '16px 0' }}>Benefício</Divider>
            <Descriptions column={{ xs: 1, sm: 2, md: 3 }} size="small">
              <Descriptions.Item label="Status">
                <Tag color={statusLabels[selectedBeneficio.status]?.color || 'default'}>
                  {statusLabels[selectedBeneficio.status]?.text || selectedBeneficio.status}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Tipo de Bem">{tipoBemLabels[selectedBeneficio.tipo_bem] || selectedBeneficio.tipo_bem}</Descriptions.Item>
              <Descriptions.Item label="Valor do Crédito">{formatCurrency(selectedBeneficio.valor_credito)}</Descriptions.Item>
              <Descriptions.Item label="Parcela">{formatCurrency(selectedBeneficio.parcela)}</Descriptions.Item>
              <Descriptions.Item label="Prazo">{selectedBeneficio.prazo_grupo ? `${selectedBeneficio.prazo_grupo} meses` : '-'}</Descriptions.Item>
              <Descriptions.Item label="Grupo">{selectedBeneficio.grupo || '-'}</Descriptions.Item>
              <Descriptions.Item label="Cota">{selectedBeneficio.cota || '-'}</Descriptions.Item>
              <Descriptions.Item label="Administradora">{selectedBeneficio.administradora?.nome || '-'}</Descriptions.Item>
              <Descriptions.Item label="Índice Correção">{selectedBeneficio.indice_correcao || 'INCC'}</Descriptions.Item>
            </Descriptions>
          </Card>
        ) : (
          <div style={{ marginTop: 24, textAlign: 'center', padding: 40 }}>
            <Empty
              description={
                !selectedClienteId
                  ? "Selecione um cliente para ver seus benefícios"
                  : beneficiosFiltrados.length === 0
                    ? "Este cliente não possui benefícios cadastrados"
                    : "Selecione um benefício para gerar o contrato ou termo de adesão"
              }
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
          </div>
        )}
      </Card>
    </div>
  )
}

export default Relatorios
