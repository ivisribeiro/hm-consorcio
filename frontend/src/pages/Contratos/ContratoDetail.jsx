import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card, Descriptions, Tag, Button, Space, Steps, Checkbox, message, Modal,
  Input, Spin, Row, Col, Divider, Typography, Alert
} from 'antd'
import {
  ArrowLeftOutlined, FilePdfOutlined, SendOutlined, CheckCircleOutlined,
  CloseCircleOutlined, FileProtectOutlined
} from '@ant-design/icons'
import { contratosApi } from '../../api/contratos'

const { Title, Text } = Typography
const { TextArea } = Input

const statusConfig = {
  gerado: { label: 'Gerado', color: 'blue', step: 0 },
  enviado_assinatura: { label: 'Enviado p/ Assinatura', color: 'orange', step: 1 },
  assinado: { label: 'Assinado', color: 'green', step: 2 },
  registrado: { label: 'Registrado', color: 'cyan', step: 3 },
  cancelado: { label: 'Cancelado', color: 'red', step: -1 },
}

const ContratoDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [contrato, setContrato] = useState(null)
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)
  const [cancelModalVisible, setCancelModalVisible] = useState(false)
  const [motivoCancelamento, setMotivoCancelamento] = useState('')

  useEffect(() => {
    loadContrato()
  }, [id])

  const loadContrato = async () => {
    setLoading(true)
    try {
      const data = await contratosApi.get(id)
      setContrato(data)
    } catch (error) {
      message.error('Erro ao carregar contrato')
      navigate('/contratos')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateStatus = async (newStatus, motivo = null) => {
    setUpdating(true)
    try {
      const data = { status: newStatus }
      if (motivo) data.motivo_cancelamento = motivo
      await contratosApi.updateStatus(id, data)
      message.success('Status atualizado com sucesso')
      loadContrato()
      setCancelModalVisible(false)
      setMotivoCancelamento('')
    } catch (error) {
      message.error(error.response?.data?.detail || 'Erro ao atualizar status')
    } finally {
      setUpdating(false)
    }
  }

  const handleUpdateAssinatura = async (field, value) => {
    setUpdating(true)
    try {
      await contratosApi.updateAssinaturas(id, { [field]: value })
      message.success('Assinatura registrada')
      loadContrato()
    } catch (error) {
      message.error('Erro ao registrar assinatura')
    } finally {
      setUpdating(false)
    }
  }

  const handleDownloadPdf = async () => {
    try {
      const blob = await contratosApi.downloadPdf(id)
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
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatCPF = (cpf) => {
    if (!cpf) return '-'
    const cleaned = cpf.replace(/\D/g, '')
    if (cleaned.length === 11) {
      return `${cleaned.slice(0,3)}.${cleaned.slice(3,6)}.${cleaned.slice(6,9)}-${cleaned.slice(9)}`
    }
    return cpf
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 100 }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!contrato) {
    return null
  }

  const statusInfo = statusConfig[contrato.status] || { label: contrato.status, color: 'default', step: 0 }
  const isCanceled = contrato.status === 'cancelado'
  const isRegistered = contrato.status === 'registrado'

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/contratos')}>
            Voltar
          </Button>
          <Title level={2} style={{ margin: 0 }}>
            Contrato #{contrato.numero}
          </Title>
          <Tag color={statusInfo.color} style={{ fontSize: 14, padding: '4px 12px' }}>
            {statusInfo.label}
          </Tag>
        </Space>
        <Button type="primary" icon={<FilePdfOutlined />} onClick={handleDownloadPdf}>
          Download PDF
        </Button>
      </div>

      {isCanceled && (
        <Alert
          message="Contrato Cancelado"
          description={contrato.motivo_cancelamento || 'Sem motivo informado'}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {/* Steps do Workflow */}
      {!isCanceled && (
        <Card style={{ marginBottom: 16 }}>
          <Steps
            current={statusInfo.step}
            items={[
              { title: 'Gerado', description: formatDate(contrato.data_geracao) },
              { title: 'Enviado', description: formatDate(contrato.data_envio) },
              { title: 'Assinado', description: formatDate(contrato.data_assinatura) },
              { title: 'Registrado', description: formatDate(contrato.data_registro) },
            ]}
          />
        </Card>
      )}

      <Row gutter={16}>
        {/* Dados do Contrato */}
        <Col xs={24} lg={12}>
          <Card title="Dados do Contrato" style={{ marginBottom: 16 }}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Numero">{contrato.numero}</Descriptions.Item>
              <Descriptions.Item label="Valor do Credito">{formatCurrency(contrato.valor_credito)}</Descriptions.Item>
              <Descriptions.Item label="Parcela">{formatCurrency(contrato.parcela)}</Descriptions.Item>
              <Descriptions.Item label="Prazo">{contrato.prazo} meses</Descriptions.Item>
              <Descriptions.Item label="Taxa de Administracao">{contrato.taxa_administracao}%</Descriptions.Item>
              <Descriptions.Item label="Fundo de Reserva">{contrato.fundo_reserva}%</Descriptions.Item>
            </Descriptions>
          </Card>

          {/* Dados do Cliente */}
          <Card title="Dados do Cliente" style={{ marginBottom: 16 }}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Nome">{contrato.cliente?.nome || '-'}</Descriptions.Item>
              <Descriptions.Item label="CPF">{formatCPF(contrato.cliente?.cpf)}</Descriptions.Item>
              <Descriptions.Item label="Telefone">{contrato.cliente?.telefone || '-'}</Descriptions.Item>
              <Descriptions.Item label="Email">{contrato.cliente?.email || '-'}</Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        {/* Assinaturas e Acoes */}
        <Col xs={24} lg={12}>
          {/* Assinaturas */}
          <Card title="Controle de Assinaturas" style={{ marginBottom: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Checkbox
                checked={contrato.assinado_cliente}
                onChange={(e) => handleUpdateAssinatura('assinado_cliente', e.target.checked)}
                disabled={isCanceled || isRegistered || updating}
              >
                <Text strong>Cliente</Text>
              </Checkbox>
              <Checkbox
                checked={contrato.assinado_representante}
                onChange={(e) => handleUpdateAssinatura('assinado_representante', e.target.checked)}
                disabled={isCanceled || isRegistered || updating}
              >
                <Text strong>Representante</Text>
              </Checkbox>
              <Checkbox
                checked={contrato.assinado_testemunha1}
                onChange={(e) => handleUpdateAssinatura('assinado_testemunha1', e.target.checked)}
                disabled={isCanceled || isRegistered || updating}
              >
                <Text strong>Testemunha 1</Text>
              </Checkbox>
              <Checkbox
                checked={contrato.assinado_testemunha2}
                onChange={(e) => handleUpdateAssinatura('assinado_testemunha2', e.target.checked)}
                disabled={isCanceled || isRegistered || updating}
              >
                <Text strong>Testemunha 2</Text>
              </Checkbox>
            </Space>
          </Card>

          {/* Acoes */}
          <Card title="Acoes" style={{ marginBottom: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              {contrato.status === 'gerado' && (
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={() => handleUpdateStatus('enviado_assinatura')}
                  loading={updating}
                  block
                >
                  Marcar como Enviado para Assinatura
                </Button>
              )}

              {contrato.status === 'enviado_assinatura' && (
                <Button
                  type="primary"
                  icon={<CheckCircleOutlined />}
                  onClick={() => handleUpdateStatus('assinado')}
                  loading={updating}
                  block
                  style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
                >
                  Marcar como Assinado
                </Button>
              )}

              {contrato.status === 'assinado' && (
                <Button
                  type="primary"
                  icon={<FileProtectOutlined />}
                  onClick={() => handleUpdateStatus('registrado')}
                  loading={updating}
                  block
                  style={{ backgroundColor: '#13c2c2', borderColor: '#13c2c2' }}
                >
                  Marcar como Registrado
                </Button>
              )}

              {!isCanceled && !isRegistered && (
                <Button
                  danger
                  icon={<CloseCircleOutlined />}
                  onClick={() => setCancelModalVisible(true)}
                  block
                >
                  Cancelar Contrato
                </Button>
              )}
            </Space>
          </Card>

          {/* Observacoes */}
          {contrato.observacoes && (
            <Card title="Observacoes" style={{ marginBottom: 16 }}>
              <Text>{contrato.observacoes}</Text>
            </Card>
          )}
        </Col>
      </Row>

      {/* Modal de Cancelamento */}
      <Modal
        title="Cancelar Contrato"
        open={cancelModalVisible}
        onOk={() => handleUpdateStatus('cancelado', motivoCancelamento)}
        onCancel={() => {
          setCancelModalVisible(false)
          setMotivoCancelamento('')
        }}
        okText="Confirmar Cancelamento"
        cancelText="Voltar"
        okButtonProps={{ danger: true, loading: updating }}
      >
        <p>Tem certeza que deseja cancelar este contrato?</p>
        <TextArea
          placeholder="Motivo do cancelamento (opcional)"
          value={motivoCancelamento}
          onChange={(e) => setMotivoCancelamento(e.target.value)}
          rows={4}
        />
      </Modal>
    </div>
  )
}

export default ContratoDetail
