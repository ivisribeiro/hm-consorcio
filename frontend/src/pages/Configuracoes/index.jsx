import { useState, useEffect } from 'react'
import { Card, Tabs, Form, Input, Switch, Button, message, Spin, Row, Col, Typography, InputNumber, ColorPicker } from 'antd'
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons'
import { configuracoesApi } from '../../api/configuracoes'

const { Title } = Typography

const Configuracoes = () => {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [empresaForm] = Form.useForm()
  const [pdfForm] = Form.useForm()
  const [sistemaForm] = Form.useForm()

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    setLoading(true)
    try {
      const [empresa, pdf, sistema] = await Promise.all([
        configuracoesApi.getEmpresa().catch(() => ({})),
        configuracoesApi.getPdf().catch(() => ({})),
        configuracoesApi.getSistema().catch(() => ({})),
      ])
      empresaForm.setFieldsValue(empresa)
      pdfForm.setFieldsValue({
        ...pdf,
        cor_header: pdf.cor_header || '#2E7D32',
        cor_section: pdf.cor_section || '#E8F5E9',
      })
      sistemaForm.setFieldsValue(sistema)
    } catch (error) {
      message.error('Erro ao carregar configuracoes')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveEmpresa = async (values) => {
    setSaving(true)
    try {
      await configuracoesApi.updateEmpresa(values)
      message.success('Configuracoes da empresa salvas com sucesso')
    } catch (error) {
      message.error('Erro ao salvar configuracoes')
    } finally {
      setSaving(false)
    }
  }

  const handleSavePdf = async (values) => {
    setSaving(true)
    try {
      // Converter cores para string hex se necessario
      const data = {
        ...values,
        cor_header: typeof values.cor_header === 'object' ? values.cor_header.toHexString() : values.cor_header,
        cor_section: typeof values.cor_section === 'object' ? values.cor_section.toHexString() : values.cor_section,
      }
      await configuracoesApi.updatePdf(data)
      message.success('Configuracoes de PDF salvas com sucesso')
    } catch (error) {
      message.error('Erro ao salvar configuracoes')
    } finally {
      setSaving(false)
    }
  }

  const handleSaveSistema = async (values) => {
    setSaving(true)
    try {
      await configuracoesApi.updateSistema(values)
      message.success('Configuracoes do sistema salvas com sucesso')
    } catch (error) {
      message.error('Erro ao salvar configuracoes')
    } finally {
      setSaving(false)
    }
  }

  const handleSeedConfigs = async () => {
    try {
      await configuracoesApi.seed()
      message.success('Configuracoes padrao criadas')
      loadSettings()
    } catch (error) {
      message.error('Erro ao criar configuracoes padrao')
    }
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 100 }}>
        <Spin size="large" />
      </div>
    )
  }

  const items = [
    {
      key: 'empresa',
      label: 'Dados da Empresa',
      children: (
        <Form form={empresaForm} layout="vertical" onFinish={handleSaveEmpresa}>
          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item name="nome" label="Nome Fantasia" rules={[{ required: true, message: 'Obrigatorio' }]}>
                <Input placeholder="HM Capital" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item name="razao_social" label="Razao Social">
                <Input placeholder="Razao social completa" />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="cnpj" label="CNPJ">
                <Input placeholder="00.000.000/0001-00" />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="telefone" label="Telefone">
                <Input placeholder="(11) 99999-9999" />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="email" label="Email">
                <Input type="email" placeholder="contato@empresa.com" />
              </Form.Item>
            </Col>
            <Col xs={24}>
              <Form.Item name="endereco" label="Endereco">
                <Input placeholder="Rua, numero, complemento" />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="cidade" label="Cidade">
                <Input placeholder="Sao Paulo" />
              </Form.Item>
            </Col>
            <Col xs={24} md={4}>
              <Form.Item name="estado" label="Estado">
                <Input placeholder="SP" maxLength={2} />
              </Form.Item>
            </Col>
            <Col xs={24} md={6}>
              <Form.Item name="cep" label="CEP">
                <Input placeholder="00000-000" />
              </Form.Item>
            </Col>
            <Col xs={24} md={6}>
              <Form.Item name="site" label="Site">
                <Input placeholder="www.empresa.com.br" />
              </Form.Item>
            </Col>
          </Row>
          <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={saving}>
            Salvar Dados da Empresa
          </Button>
        </Form>
      ),
    },
    {
      key: 'pdf',
      label: 'Configuracoes de PDF',
      children: (
        <Form form={pdfForm} layout="vertical" onFinish={handleSavePdf}>
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item name="cor_header" label="Cor do Cabecalho">
                <ColorPicker format="hex" />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="cor_section" label="Cor das Secoes">
                <ColorPicker format="hex" />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="show_logo" label="Exibir Logo" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
            <Col xs={24}>
              <Form.Item name="footer_text" label="Texto do Rodape">
                <Input placeholder="HM Capital - CRM Consorcios" />
              </Form.Item>
            </Col>
          </Row>
          <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={saving}>
            Salvar Configuracoes de PDF
          </Button>
        </Form>
      ),
    },
    {
      key: 'sistema',
      label: 'Sistema',
      children: (
        <Form form={sistemaForm} layout="vertical" onFinish={handleSaveSistema}>
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item name="items_per_page" label="Itens por Pagina">
                <InputNumber min={5} max={100} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="session_timeout_minutes" label="Timeout da Sessao (minutos)">
                <InputNumber min={5} max={480} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="enable_notifications" label="Habilitar Notificacoes" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="default_currency" label="Moeda Padrao">
                <Input placeholder="BRL" maxLength={3} />
              </Form.Item>
            </Col>
          </Row>
          <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={saving}>
            Salvar Configuracoes do Sistema
          </Button>
        </Form>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={2}>Configuracoes</Title>
        <Button icon={<ReloadOutlined />} onClick={handleSeedConfigs}>
          Restaurar Padrao
        </Button>
      </div>

      <Card>
        <Tabs items={items} />
      </Card>
    </div>
  )
}

export default Configuracoes
