import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Card, Descriptions, Tag, Button, Space, Steps, message, Spin, Modal,
  Input, Row, Col, Timeline, Divider, Typography, Alert, Tooltip
} from 'antd'
import {
  ArrowLeftOutlined, CheckOutlined, CloseOutlined, SendOutlined,
  FileTextOutlined, EditOutlined, SafetyCertificateOutlined,
  CheckCircleOutlined, ClockCircleOutlined, ExclamationCircleOutlined,
  FilePdfOutlined, RollbackOutlined, ArrowRightOutlined, UserOutlined
} from '@ant-design/icons'
import { beneficiosApi } from '../../api/beneficios'
import { clientesApi } from '../../api/clientes'
import { relatoriosApi } from '../../api/relatorios'

const { Text, Title } = Typography
const { TextArea } = Input

const statusFlow = [
  'rascunho', 'proposto', 'aceito', 'contrato_gerado', 'contrato_assinado',
  'aguardando_cadastro', 'cadastrado', 'termo_gerado', 'ativo'
]

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

const statusColors = {
  rascunho: 'default',
  proposto: 'processing',
  aceito: 'success',
  rejeitado: 'error',
  contrato_gerado: 'warning',
  contrato_assinado: 'cyan',
  aguardando_cadastro: 'purple',
  cadastrado: 'geekblue',
  termo_gerado: 'blue',
  ativo: 'green',
  cancelado: 'red',
}

const tipoBemLabels = { imovel: 'Imóvel', carro: 'Carro', moto: 'Moto' }

const BeneficioDetail = () => {
  const navigate = useNavigate()
  const { id } = useParams()
  const [beneficio, setBeneficio] = useState(null)
  const [cliente, setCliente] = useState(null)
  const [historico, setHistorico] = useState([])
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)
  const [downloadingPdf, setDownloadingPdf] = useState(false)

  // Modals
  const [cadastroModal, setCadastroModal] = useState(false)
  const [rejeicaoModal, setRejeicaoModal] = useState(false)
  const [cancelamentoModal, setCancelamentoModal] = useState(false)

  // Form fields
  const [grupo, setGrupo] = useState('')
  const [cota, setCota] = useState('')
  const [motivoRejeicao, setMotivoRejeicao] = useState('')
  const [motivoCancelamento, setMotivoCancelamento] = useState('')

  useEffect(() => {
    loadData()
  }, [id])

  const loadData = async () => {
    setLoading(true)
    try {
      const [beneficioData, historicoData] = await Promise.all([
        beneficiosApi.get(id),
        beneficiosApi.getHistorico(id)
      ])
      setBeneficio(beneficioData)
      setHistorico(historicoData)

      const clienteData = await clientesApi.get(beneficioData.cliente_id)
      setCliente(clienteData)
    } catch (error) {
      message.error('Erro ao carregar benefício')
      navigate('/beneficios')
    } finally {
      setLoading(false)
    }
  }

  const handleStatusUpdate = async (newStatus, extra = {}) => {
    setUpdating(true)
    try {
      await beneficiosApi.updateStatus(id, { status: newStatus, ...extra })
      message.success('Status atualizado com sucesso!')
      loadData()
    } catch (error) {
      message.error(error.response?.data?.detail || 'Erro ao atualizar status')
    } finally {
      setUpdating(false)
    }
  }

  const handleRejeicao = async () => {
    await handleStatusUpdate('rejeitado', { motivo_rejeicao: motivoRejeicao })
    setRejeicaoModal(false)
    setMotivoRejeicao('')
  }

  const handleCancelamento = async () => {
    await handleStatusUpdate('cancelado', { motivo_cancelamento: motivoCancelamento })
    setCancelamentoModal(false)
    setMotivoCancelamento('')
  }

  const handleDownloadPdf = async () => {
    setDownloadingPdf(true)
    try {
      const blob = await relatoriosApi.gerarPdfBeneficio(id)
      const clienteNome = cliente?.nome || 'cliente'
      relatoriosApi.downloadPdf(blob, `proposta_${id}_${clienteNome.replace(/\s+/g, '_')}.pdf`)
      message.success('PDF gerado com sucesso!')
    } catch (error) {
      message.error('Erro ao gerar PDF')
    } finally {
      setDownloadingPdf(false)
    }
  }

  const handleCadastroGrupoCota = async () => {
    if (!grupo || !cota) {
      message.error('Informe o grupo e a cota')
      return
    }
    setUpdating(true)
    try {
      await beneficiosApi.update(id, { grupo, cota })
      await beneficiosApi.updateStatus(id, { status: 'cadastrado' })
      message.success('Grupo e cota registrados com sucesso!')
      setCadastroModal(false)
      setGrupo('')
      setCota('')
      loadData()
    } catch (error) {
      message.error('Erro ao registrar grupo e cota')
    } finally {
      setUpdating(false)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return null
    return new Date(dateString).toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value || 0)
  }

  // Cores e labels para ações do histórico
  const acaoColors = {
    avancou: 'green',
    voltou: 'orange',
    rejeitou: 'red',
    cancelou: 'red',
  }

  const acaoLabels = {
    avancou: 'Avançou',
    voltou: 'Voltou',
    rejeitou: 'Rejeitou',
    cancelou: 'Cancelou',
  }

  // Monta o timeline de eventos a partir do histórico
  const getTimeline = () => {
    const events = []

    // Evento de criação do benefício
    if (beneficio?.created_at) {
      events.push({
        color: 'blue',
        children: (
          <>
            <Text strong>Benefício criado</Text>
            <br />
            <Text type="secondary">{formatDate(beneficio.created_at)}</Text>
          </>
        ),
      })
    }

    // Histórico de mudanças de status (invertido pois vem desc da API)
    const historicoOrdenado = [...historico].reverse()

    historicoOrdenado.forEach((h) => {
      const color = acaoColors[h.acao] || 'blue'
      const statusAnteriorLabel = h.status_anterior ? statusLabels[h.status_anterior] : '-'
      const statusNovoLabel = statusLabels[h.status_novo] || h.status_novo

      events.push({
        color,
        children: (
          <>
            <Text strong>
              {acaoLabels[h.acao] || h.acao}: {statusAnteriorLabel} {'->'} {statusNovoLabel}
            </Text>
            <br />
            <Space size="small">
              <UserOutlined style={{ fontSize: 12 }} />
              <Text type="secondary" style={{ fontSize: 12 }}>
                {h.usuario_nome || 'Sistema'}
              </Text>
              <Text type="secondary" style={{ fontSize: 12 }}>
                | {formatDate(h.created_at)}
              </Text>
            </Space>
            {h.observacao && (
              <>
                <br />
                <Text type="danger" style={{ fontSize: 12 }}>Motivo: {h.observacao}</Text>
              </>
            )}
          </>
        ),
      })
    })

    return events
  }

  // Mapa de status anterior para poder voltar
  const previousStatus = {
    proposto: 'rascunho',
    aceito: 'proposto',
    contrato_gerado: 'aceito',
    contrato_assinado: 'contrato_gerado',
    aguardando_cadastro: 'contrato_assinado',
    cadastrado: 'aguardando_cadastro',
    termo_gerado: 'cadastrado',
  }

  const getActionButtons = () => {
    if (!beneficio) return null

    const buttons = []
    const prevStatus = previousStatus[beneficio.status]

    // Botão de voltar (se não for rascunho ou status final)
    if (prevStatus && !['ativo', 'cancelado', 'rejeitado'].includes(beneficio.status)) {
      buttons.push(
        <Tooltip key="voltar" title={`Voltar para ${statusLabels[prevStatus]}`}>
          <Button
            icon={<RollbackOutlined />}
            onClick={() => handleStatusUpdate(prevStatus)}
            loading={updating}
          >
            Voltar
          </Button>
        </Tooltip>
      )
    }

    switch (beneficio.status) {
      case 'rascunho':
        buttons.push(
          <Button
            key="propor"
            type="primary"
            icon={<ArrowRightOutlined />}
            onClick={() => handleStatusUpdate('proposto')}
            loading={updating}
          >
            Enviar Proposta
          </Button>
        )
        break

      case 'proposto':
        buttons.push(
          <Button
            key="aceitar"
            type="primary"
            icon={<ArrowRightOutlined />}
            onClick={() => handleStatusUpdate('aceito')}
            loading={updating}
          >
            Cliente Aceitou
          </Button>,
          <Button
            key="rejeitar"
            danger
            icon={<CloseOutlined />}
            onClick={() => setRejeicaoModal(true)}
            loading={updating}
          >
            Cliente Rejeitou
          </Button>
        )
        break

      case 'aceito':
        buttons.push(
          <Button
            key="contrato"
            type="primary"
            icon={<ArrowRightOutlined />}
            onClick={() => handleStatusUpdate('contrato_gerado')}
            loading={updating}
          >
            Gerar Contrato
          </Button>
        )
        break

      case 'contrato_gerado':
        buttons.push(
          <Button
            key="assinar"
            type="primary"
            icon={<ArrowRightOutlined />}
            onClick={() => handleStatusUpdate('contrato_assinado')}
            loading={updating}
          >
            Registrar Assinatura do Contrato
          </Button>
        )
        break

      case 'contrato_assinado':
        buttons.push(
          <Button
            key="admin"
            type="primary"
            icon={<ArrowRightOutlined />}
            onClick={() => handleStatusUpdate('aguardando_cadastro')}
            loading={updating}
          >
            Enviar para Administradora
          </Button>
        )
        break

      case 'aguardando_cadastro':
        buttons.push(
          <Button
            key="cadastro"
            type="primary"
            icon={<ArrowRightOutlined />}
            onClick={() => setCadastroModal(true)}
            loading={updating}
          >
            Registrar Grupo e Cota
          </Button>
        )
        break

      case 'cadastrado':
        buttons.push(
          <Button
            key="termo"
            type="primary"
            icon={<ArrowRightOutlined />}
            onClick={() => handleStatusUpdate('termo_gerado')}
            loading={updating}
          >
            Gerar Termo de Adesão
          </Button>
        )
        break

      case 'termo_gerado':
        buttons.push(
          <Button
            key="ativar"
            type="primary"
            icon={<CheckCircleOutlined />}
            onClick={() => handleStatusUpdate('ativo')}
            loading={updating}
            style={{ background: '#52c41a', borderColor: '#52c41a' }}
          >
            Ativar Benefício
          </Button>
        )
        break
    }

    // Botão de cancelar (exceto se já finalizado)
    if (!['ativo', 'cancelado', 'rejeitado'].includes(beneficio.status)) {
      buttons.push(
        <Button
          key="cancelar"
          danger
          icon={<ExclamationCircleOutlined />}
          onClick={() => setCancelamentoModal(true)}
          loading={updating}
        >
          Cancelar Benefício
        </Button>
      )
    }

    return buttons
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <Spin size="large" />
      </div>
    )
  }

  const currentStep = statusFlow.indexOf(beneficio.status)

  return (
    <div>
      <Card
        title={
          <Space>
            <span>Benefício #{beneficio.id}</span>
            <Tag color={statusColors[beneficio.status]} style={{ marginLeft: 8 }}>
              {statusLabels[beneficio.status]}
            </Tag>
          </Space>
        }
        extra={
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/beneficios')}>
            Voltar
          </Button>
        }
      >
        {/* Alerta se rejeitado ou cancelado */}
        {beneficio.status === 'rejeitado' && (
          <Alert
            message="Proposta Rejeitada"
            description={beneficio.motivo_rejeicao || 'Cliente não aceitou a proposta'}
            type="error"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}

        {beneficio.status === 'cancelado' && (
          <Alert
            message="Benefício Cancelado"
            description={beneficio.motivo_cancelamento || 'Benefício foi cancelado'}
            type="error"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}

        {/* Status Steps */}
        {!['rejeitado', 'cancelado'].includes(beneficio.status) && (
          <Steps
            current={currentStep >= 0 ? currentStep : 0}
            items={statusFlow.map((s) => ({ title: statusLabels[s] }))}
            size="small"
            style={{ marginBottom: 24 }}
          />
        )}

        <Row gutter={[16, 16]}>
          {/* Dados do Benefício */}
          <Col xs={24} lg={12}>
            <Card title="Dados do Benefício" size="small" type="inner">
              <Descriptions column={1} size="small">
                <Descriptions.Item label="Tipo de Bem">
                  <Tag>{tipoBemLabels[beneficio.tipo_bem]}</Tag>
                </Descriptions.Item>
                <Descriptions.Item label="Valor do Crédito">
                  <Text strong style={{ fontSize: 16 }}>{formatCurrency(beneficio.valor_credito)}</Text>
                </Descriptions.Item>
                <Descriptions.Item label="Parcela Mensal">
                  <Text strong>{formatCurrency(beneficio.parcela)}</Text>
                </Descriptions.Item>
                <Descriptions.Item label="Prazo">{beneficio.prazo_grupo} meses</Descriptions.Item>
                <Descriptions.Item label="Fundo de Reserva">{beneficio.fundo_reserva}%</Descriptions.Item>
                <Descriptions.Item label="Taxa Administração">{beneficio.taxa_administracao}%</Descriptions.Item>
                <Descriptions.Item label="Índice de Correção">{beneficio.indice_correcao}</Descriptions.Item>
                {beneficio.grupo && (
                  <Descriptions.Item label="Grupo">
                    <Tag color="blue">{beneficio.grupo}</Tag>
                  </Descriptions.Item>
                )}
                {beneficio.cota && (
                  <Descriptions.Item label="Cota">
                    <Tag color="green">{beneficio.cota}</Tag>
                  </Descriptions.Item>
                )}
              </Descriptions>
            </Card>
          </Col>

          {/* Dados do Cliente */}
          <Col xs={24} lg={12}>
            {cliente && (
              <Card title="Dados do Cliente" size="small" type="inner">
                <Descriptions column={1} size="small">
                  <Descriptions.Item label="Nome">{cliente.nome}</Descriptions.Item>
                  <Descriptions.Item label="CPF">{cliente.cpf}</Descriptions.Item>
                  <Descriptions.Item label="Telefone">{cliente.telefone}</Descriptions.Item>
                  <Descriptions.Item label="Email">{cliente.email || '-'}</Descriptions.Item>
                  <Descriptions.Item label="Salário">
                    {cliente.salario ? formatCurrency(cliente.salario) : '-'}
                  </Descriptions.Item>
                  <Descriptions.Item label="Cidade">
                    {cliente.cidade ? `${cliente.cidade}/${cliente.estado}` : '-'}
                  </Descriptions.Item>
                </Descriptions>
                <Button
                  type="link"
                  size="small"
                  onClick={() => navigate(`/clientes/${cliente.id}`)}
                  style={{ padding: 0, marginTop: 8 }}
                >
                  Ver cadastro completo
                </Button>
              </Card>
            )}
          </Col>
        </Row>

        <Divider />

        {/* Ações */}
        <Card title="Ações" size="small" type="inner" style={{ marginBottom: 16 }}>
          <Space wrap>
            {getActionButtons()}
            <Button
              icon={<FilePdfOutlined />}
              onClick={handleDownloadPdf}
              loading={downloadingPdf}
            >
              Gerar PDF
            </Button>
          </Space>
        </Card>

        {/* Timeline de eventos */}
        <Card
          title={
            <Space>
              <ClockCircleOutlined />
              <span>Histórico</span>
            </Space>
          }
          size="small"
          type="inner"
        >
          <Timeline items={getTimeline()} />
        </Card>

        {/* Observações */}
        {beneficio.observacoes && (
          <Card title="Observações" size="small" type="inner" style={{ marginTop: 16 }}>
            <Text>{beneficio.observacoes}</Text>
          </Card>
        )}
      </Card>

      {/* Modal de Registro de Grupo e Cota */}
      <Modal
        title="Registrar Grupo e Cota"
        open={cadastroModal}
        onOk={handleCadastroGrupoCota}
        onCancel={() => setCadastroModal(false)}
        confirmLoading={updating}
        okText="Confirmar"
      >
        <p>Informe os dados recebidos da administradora:</p>
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <div>
            <Text type="secondary">Grupo</Text>
            <Input
              placeholder="Ex: 1234"
              value={grupo}
              onChange={(e) => setGrupo(e.target.value)}
            />
          </div>
          <div>
            <Text type="secondary">Cota</Text>
            <Input
              placeholder="Ex: 0567"
              value={cota}
              onChange={(e) => setCota(e.target.value)}
            />
          </div>
        </Space>
      </Modal>

      {/* Modal de Rejeição */}
      <Modal
        title="Registrar Rejeição"
        open={rejeicaoModal}
        onOk={handleRejeicao}
        onCancel={() => setRejeicaoModal(false)}
        confirmLoading={updating}
        okText="Confirmar Rejeição"
        okButtonProps={{ danger: true }}
      >
        <p>O cliente rejeitou a proposta. Informe o motivo (opcional):</p>
        <TextArea
          rows={4}
          placeholder="Motivo da rejeição..."
          value={motivoRejeicao}
          onChange={(e) => setMotivoRejeicao(e.target.value)}
        />
      </Modal>

      {/* Modal de Cancelamento */}
      <Modal
        title="Cancelar Benefício"
        open={cancelamentoModal}
        onOk={handleCancelamento}
        onCancel={() => setCancelamentoModal(false)}
        confirmLoading={updating}
        okText="Confirmar Cancelamento"
        okButtonProps={{ danger: true }}
      >
        <Alert
          message="Atenção"
          description="Esta ação não pode ser desfeita. O benefício será cancelado permanentemente."
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
        <p>Informe o motivo do cancelamento:</p>
        <TextArea
          rows={4}
          placeholder="Motivo do cancelamento..."
          value={motivoCancelamento}
          onChange={(e) => setMotivoCancelamento(e.target.value)}
        />
      </Modal>
    </div>
  )
}

export default BeneficioDetail
