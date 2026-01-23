import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Row, Col, Card, Statistic, Typography, List, Tag, Progress, Spin, Button, Space } from 'antd'
import {
  TeamOutlined,
  GiftOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  DollarOutlined,
  UserOutlined,
  ClockCircleOutlined,
  PlusOutlined,
  SearchOutlined,
  FilePdfOutlined,
} from '@ant-design/icons'
import { useAuth } from '../../contexts/AuthContext'
import { dashboardApi } from '../../api/dashboard'

const { Title, Text } = Typography

const statusColors = {
  rascunho: '#d9d9d9',
  proposto: '#1890ff',
  aceito: '#52c41a',
  rejeitado: '#f5222d',
  contrato_gerado: '#faad14',
  contrato_assinado: '#13c2c2',
  aguardando_cadastro: '#eb2f96',
  cadastrado: '#722ed1',
  termo_gerado: '#2f54eb',
  ativo: '#52c41a',
  cancelado: '#8c8c8c',
}

const tipoBemColors = {
  imovel: '#1890ff',
  carro: '#52c41a',
  moto: '#faad14',
}

const Dashboard = () => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [metricas, setMetricas] = useState(null)
  const [atividades, setAtividades] = useState([])
  const [statusDistribuicao, setStatusDistribuicao] = useState([])
  const [tipoBemDistribuicao, setTipoBemDistribuicao] = useState([])
  const [vendasMensal, setVendasMensal] = useState([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metricasData, atividadesData, statusData, tipoBemData, vendasData] = await Promise.all([
          dashboardApi.getMetricas(),
          dashboardApi.getAtividadesRecentes(8),
          dashboardApi.getStatusDistribuicao().catch(() => []),
          dashboardApi.getTipoBemDistribuicao().catch(() => []),
          dashboardApi.getVendasMensal(6).catch(() => []),
        ])
        setMetricas(metricasData)
        setAtividades(atividadesData)
        setStatusDistribuicao(statusData)
        setTipoBemDistribuicao(tipoBemData)
        setVendasMensal(vendasData)
      } catch (error) {
        console.error('Erro ao carregar dashboard:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value || 0)
  }

  const formatDate = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const stats = [
    {
      title: 'Total de Clientes',
      value: metricas?.total_clientes || 0,
      icon: <TeamOutlined style={{ fontSize: 24, color: '#1890ff' }} />,
      color: '#e6f7ff',
    },
    {
      title: 'Beneficios Ativos',
      value: metricas?.beneficios_ativos || 0,
      icon: <GiftOutlined style={{ fontSize: 24, color: '#52c41a' }} />,
      color: '#f6ffed',
    },
    {
      title: 'Contratos Pendentes',
      value: metricas?.contratos_pendentes || 0,
      icon: <FileTextOutlined style={{ fontSize: 24, color: '#faad14' }} />,
      color: '#fffbe6',
    },
    {
      title: 'Vendas Finalizadas',
      value: metricas?.vendas_concluidas || 0,
      icon: <CheckCircleOutlined style={{ fontSize: 24, color: '#722ed1' }} />,
      color: '#f9f0ff',
    },
  ]

  // Calcula o total para porcentagens do pipeline
  const totalPipeline = metricas?.pipeline?.reduce((acc, item) => acc + item.quantidade, 0) || 0
  const totalTipoBem = tipoBemDistribuicao.reduce((acc, item) => acc + item.quantidade, 0) || 0

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div>
      {/* Header com acoes rapidas */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Title level={2} style={{ margin: 0 }}>
            Ola, {user?.nome}!
          </Title>
        </Col>
        <Col>
          <Space wrap>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => navigate('/clientes/novo')}
            >
              Novo Cliente
            </Button>
            <Button
              icon={<GiftOutlined />}
              onClick={() => navigate('/beneficios/novo')}
            >
              Novo Beneficio
            </Button>
            <Button
              icon={<SearchOutlined />}
              onClick={() => navigate('/clientes')}
            >
              Buscar Cliente
            </Button>
            <Button
              icon={<FilePdfOutlined />}
              onClick={() => navigate('/relatorios')}
            >
              Relatorios
            </Button>
          </Space>
        </Col>
      </Row>

      {/* Cards de metricas */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {stats.map((stat, index) => (
          <Col xs={24} sm={12} lg={6} key={index}>
            <Card style={{ background: stat.color }}>
              <Row align="middle" justify="space-between">
                <Col>
                  <Statistic
                    title={stat.title}
                    value={stat.value}
                    valueStyle={{ color: '#333' }}
                  />
                </Col>
                <Col>{stat.icon}</Col>
              </Row>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Card de valor total */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24}>
          <Card style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <Row align="middle" justify="center">
              <Col>
                <Statistic
                  title={<span style={{ color: 'rgba(255,255,255,0.8)' }}>Valor Total em Creditos Ativos</span>}
                  value={formatCurrency(metricas?.valor_creditos)}
                  valueStyle={{ color: '#fff', fontSize: 32 }}
                  prefix={<DollarOutlined />}
                />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Graficos - Distribuicao por Status e Tipo de Bem */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {/* Distribuicao por Status */}
        <Col xs={24} lg={12}>
          <Card title="Distribuicao por Status">
            {statusDistribuicao.length > 0 ? (
              <div>
                {statusDistribuicao
                  .filter(item => item.quantidade > 0)
                  .sort((a, b) => b.quantidade - a.quantidade)
                  .map((item) => (
                    <div key={item.status} style={{ marginBottom: 12 }}>
                      <Row justify="space-between" align="middle" style={{ marginBottom: 4 }}>
                        <Col>
                          <Tag color={statusColors[item.status] || '#8c8c8c'}>{item.label}</Tag>
                        </Col>
                        <Col>
                          <Text strong>{item.quantidade}</Text>
                          <Text type="secondary" style={{ marginLeft: 8 }}>
                            ({formatCurrency(item.valor)})
                          </Text>
                        </Col>
                      </Row>
                      <Progress
                        percent={Math.round((item.quantidade / (statusDistribuicao.reduce((acc, i) => acc + i.quantidade, 0) || 1)) * 100)}
                        strokeColor={statusColors[item.status] || '#8c8c8c'}
                        size="small"
                      />
                    </div>
                  ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                Nenhum dado disponivel
              </div>
            )}
          </Card>
        </Col>

        {/* Distribuicao por Tipo de Bem */}
        <Col xs={24} lg={12}>
          <Card title="Distribuicao por Tipo de Bem">
            {tipoBemDistribuicao.length > 0 ? (
              <div>
                {tipoBemDistribuicao.map((item) => (
                  <div key={item.tipo} style={{ marginBottom: 16 }}>
                    <Row justify="space-between" align="middle" style={{ marginBottom: 4 }}>
                      <Col>
                        <Tag color={tipoBemColors[item.tipo] || '#8c8c8c'}>{item.label}</Tag>
                      </Col>
                      <Col>
                        <Text strong>{item.quantidade}</Text>
                        <Text type="secondary" style={{ marginLeft: 8 }}>
                          ({formatCurrency(item.valor)})
                        </Text>
                      </Col>
                    </Row>
                    <Progress
                      percent={totalTipoBem > 0 ? Math.round((item.quantidade / totalTipoBem) * 100) : 0}
                      strokeColor={tipoBemColors[item.tipo] || '#8c8c8c'}
                      size="small"
                    />
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                Nenhum dado disponivel
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* Vendas Mensais */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24}>
          <Card title="Vendas nos Ultimos 6 Meses">
            {vendasMensal.length > 0 ? (
              <Row gutter={[8, 8]}>
                {vendasMensal.map((item) => (
                  <Col xs={24} sm={12} md={8} lg={4} key={item.mes}>
                    <Card
                      size="small"
                      style={{ textAlign: 'center', background: '#fafafa' }}
                    >
                      <div style={{ fontSize: 12, color: '#666', marginBottom: 4 }}>{item.mes_label}</div>
                      <div style={{ fontSize: 20, fontWeight: 'bold', color: '#1890ff' }}>{item.quantidade}</div>
                      <div style={{ fontSize: 11, color: '#52c41a' }}>{formatCurrency(item.valor)}</div>
                    </Card>
                  </Col>
                ))}
              </Row>
            ) : (
              <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                Nenhum dado disponivel
              </div>
            )}
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Pipeline de Vendas */}
        <Col xs={24} lg={16}>
          <Card title="Pipeline de Vendas" style={{ height: '100%' }}>
            {metricas?.pipeline && metricas.pipeline.length > 0 ? (
              <div>
                {metricas.pipeline.map((item) => (
                  <div key={item.status} style={{ marginBottom: 16 }}>
                    <Row justify="space-between" align="middle" style={{ marginBottom: 4 }}>
                      <Col>
                        <Tag color={statusColors[item.status]}>{item.label}</Tag>
                      </Col>
                      <Col>
                        <Text strong>{item.quantidade}</Text>
                      </Col>
                    </Row>
                    <Progress
                      percent={totalPipeline > 0 ? Math.round((item.quantidade / totalPipeline) * 100) : 0}
                      strokeColor={statusColors[item.status]}
                      showInfo={false}
                      size="small"
                    />
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                Nenhum beneficio cadastrado ainda
              </div>
            )}
          </Card>
        </Col>

        {/* Atividades Recentes */}
        <Col xs={24} lg={8}>
          <Card title="Atividades Recentes" style={{ height: '100%' }}>
            {atividades.length > 0 ? (
              <List
                itemLayout="horizontal"
                dataSource={atividades}
                renderItem={(item) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={
                        item.tipo === 'cliente' ? (
                          <UserOutlined style={{ fontSize: 20, color: '#1890ff' }} />
                        ) : (
                          <GiftOutlined style={{ fontSize: 20, color: '#52c41a' }} />
                        )
                      }
                      title={<Text style={{ fontSize: 13 }}>{item.descricao}</Text>}
                      description={
                        <Text type="secondary" style={{ fontSize: 11 }}>
                          <ClockCircleOutlined /> {formatDate(item.data)}
                        </Text>
                      }
                    />
                  </List.Item>
                )}
              />
            ) : (
              <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                Nenhuma atividade registrada
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard
