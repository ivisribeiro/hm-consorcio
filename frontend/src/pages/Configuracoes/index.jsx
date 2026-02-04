import { useState, useEffect } from 'react'
import { Card, Tabs, Form, Input, Switch, Button, message, Spin, Row, Col, Typography, InputNumber, ColorPicker, Table, Checkbox, Tag, Modal, Space, Popconfirm } from 'antd'
import { SaveOutlined, ReloadOutlined, SafetyCertificateOutlined, PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { configuracoesApi } from '../../api/configuracoes'
import { perfisApi } from '../../api/permissoes'

const { Title } = Typography

const Configuracoes = () => {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [empresaForm] = Form.useForm()
  const [pdfForm] = Form.useForm()
  const [sistemaForm] = Form.useForm()
  const [perfilForm] = Form.useForm()

  // Permissões
  const [permissoes, setPermissoes] = useState([])
  const [perfis, setPerfis] = useState([])
  const [matriz, setMatriz] = useState({})
  const [loadingPermissoes, setLoadingPermissoes] = useState(false)
  const [savingPermissoes, setSavingPermissoes] = useState(false)

  // Modal de novo perfil
  const [modalVisible, setModalVisible] = useState(false)
  const [editingPerfil, setEditingPerfil] = useState(null)

  useEffect(() => {
    loadSettings()
    loadPermissoes()
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

  const loadPermissoes = async () => {
    setLoadingPermissoes(true)
    try {
      const data = await perfisApi.getMatriz()
      setPermissoes(data.permissoes || [])
      setPerfis(data.perfis || [])
      setMatriz(data.matriz || {})
    } catch (error) {
      // Se não tem permissões, tenta criar
      if (error.response?.status === 404 || permissoes.length === 0) {
        try {
          await perfisApi.seed()
          const data = await perfisApi.getMatriz()
          setPermissoes(data.permissoes || [])
          setPerfis(data.perfis || [])
          setMatriz(data.matriz || {})
        } catch (seedError) {
          console.error('Erro ao criar permissões padrão:', seedError)
        }
      }
    } finally {
      setLoadingPermissoes(false)
    }
  }

  const handlePermissaoChange = (perfilId, codigo, checked) => {
    const key = String(perfilId)
    setMatriz(prev => {
      const perfilPermissoes = prev[key] || []
      if (checked) {
        return { ...prev, [key]: [...perfilPermissoes, codigo] }
      } else {
        return { ...prev, [key]: perfilPermissoes.filter(p => p !== codigo) }
      }
    })
  }

  const handleSavePermissoes = async (perfilId) => {
    const key = String(perfilId)
    setSavingPermissoes(true)
    try {
      await perfisApi.updatePermissoes(perfilId, matriz[key] || [])
      const perfil = perfis.find(p => p.id === perfilId)
      message.success(`Permissões do perfil ${perfil?.nome || perfilId} salvas com sucesso`)
    } catch (error) {
      message.error('Erro ao salvar permissões')
    } finally {
      setSavingPermissoes(false)
    }
  }

  const handleSeedPermissoes = async () => {
    try {
      await perfisApi.seed()
      message.success('Permissões padrão criadas')
      loadPermissoes()
    } catch (error) {
      message.error('Erro ao criar permissões padrão')
    }
  }

  const handleNovoPerfil = () => {
    setEditingPerfil(null)
    perfilForm.resetFields()
    perfilForm.setFieldsValue({ cor: '#1890ff' })
    setModalVisible(true)
  }

  const handleEditPerfil = async (perfil) => {
    setEditingPerfil(perfil)
    try {
      const perfilCompleto = await perfisApi.get(perfil.id)
      perfilForm.setFieldsValue({
        codigo: perfilCompleto.codigo,
        nome: perfilCompleto.nome,
        descricao: perfilCompleto.descricao,
        cor: perfilCompleto.cor,
      })
      setModalVisible(true)
    } catch (error) {
      message.error('Erro ao carregar perfil')
    }
  }

  const handleDeletePerfil = async (perfilId) => {
    try {
      await perfisApi.delete(perfilId)
      message.success('Perfil excluído com sucesso')
      loadPermissoes()
    } catch (error) {
      message.error(error.response?.data?.detail || 'Erro ao excluir perfil')
    }
  }

  const handleSavePerfil = async (values) => {
    setSaving(true)
    try {
      // Converter cor para string hex se necessario
      const data = {
        ...values,
        cor: typeof values.cor === 'object' ? values.cor.toHexString() : values.cor,
      }

      if (editingPerfil) {
        await perfisApi.update(editingPerfil.id, data)
        message.success('Perfil atualizado com sucesso')
      } else {
        await perfisApi.create(data)
        message.success('Perfil criado com sucesso')
      }

      setModalVisible(false)
      perfilForm.resetFields()
      loadPermissoes()
    } catch (error) {
      message.error(error.response?.data?.detail || 'Erro ao salvar perfil')
    } finally {
      setSaving(false)
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
    {
      key: 'permissoes',
      label: (
        <span>
          <SafetyCertificateOutlined /> Perfis e Permissões
        </span>
      ),
      children: (
        <div>
          {loadingPermissoes ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: 50 }}>
              <Spin />
            </div>
          ) : permissoes.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 50 }}>
              <p>Nenhuma permissão cadastrada.</p>
              <Button type="primary" onClick={handleSeedPermissoes}>
                Criar Permissões Padrão
              </Button>
            </div>
          ) : (
            <div>
              <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  {perfis.map(perfil => (
                    <Tag key={perfil.id} color={perfil.cor || 'blue'}>
                      {perfil.nome}
                    </Tag>
                  ))}
                </div>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleNovoPerfil}>
                  Novo Perfil
                </Button>
              </div>

              <Table
                dataSource={permissoes}
                rowKey="codigo"
                pagination={false}
                size="small"
                scroll={{ x: 800 }}
                columns={[
                  {
                    title: 'Módulo',
                    dataIndex: 'modulo',
                    key: 'modulo',
                    width: 120,
                    render: (modulo) => (
                      <Tag color="default" style={{ textTransform: 'capitalize' }}>
                        {modulo}
                      </Tag>
                    ),
                    filters: [...new Set(permissoes.map(p => p.modulo))].map(m => ({ text: m, value: m })),
                    onFilter: (value, record) => record.modulo === value,
                  },
                  {
                    title: 'Permissão',
                    dataIndex: 'nome',
                    key: 'nome',
                    width: 200,
                  },
                  ...perfis.map(perfil => ({
                    title: (
                      <Space>
                        <span style={{ color: perfil.cor }}>{perfil.nome}</span>
                        {!perfil.is_system && (
                          <Button
                            type="text"
                            size="small"
                            icon={<EditOutlined />}
                            onClick={() => handleEditPerfil(perfil)}
                          />
                        )}
                      </Space>
                    ),
                    key: perfil.id,
                    width: 150,
                    align: 'center',
                    render: (_, record) => (
                      <Checkbox
                        checked={(matriz[String(perfil.id)] || []).includes(record.codigo)}
                        onChange={(e) => handlePermissaoChange(perfil.id, record.codigo, e.target.checked)}
                        disabled={perfil.codigo === 'admin'}
                      />
                    ),
                  })),
                ]}
              />

              <div style={{ marginTop: 24, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {perfis.filter(p => p.codigo !== 'admin').map(perfil => (
                  <Button
                    key={perfil.id}
                    type="primary"
                    icon={<SaveOutlined />}
                    loading={savingPermissoes}
                    onClick={() => handleSavePermissoes(perfil.id)}
                    style={{ backgroundColor: perfil.cor, borderColor: perfil.cor }}
                  >
                    Salvar {perfil.nome}
                  </Button>
                ))}
              </div>
            </div>
          )}
        </div>
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

      <Modal
        title={editingPerfil ? 'Editar Perfil' : 'Novo Perfil'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        destroyOnClose
      >
        <Form form={perfilForm} layout="vertical" onFinish={handleSavePerfil}>
          <Form.Item
            name="codigo"
            label="Código"
            rules={[{ required: true, message: 'Obrigatório' }]}
          >
            <Input placeholder="meu_perfil" disabled={!!editingPerfil} />
          </Form.Item>
          <Form.Item
            name="nome"
            label="Nome"
            rules={[{ required: true, message: 'Obrigatório' }]}
          >
            <Input placeholder="Meu Perfil Customizado" />
          </Form.Item>
          <Form.Item name="descricao" label="Descrição">
            <Input.TextArea rows={2} placeholder="Descrição do perfil" />
          </Form.Item>
          <Form.Item name="cor" label="Cor">
            <ColorPicker format="hex" />
          </Form.Item>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            {editingPerfil && !editingPerfil.is_system && (
              <Popconfirm
                title="Excluir perfil?"
                description="Esta ação não pode ser desfeita."
                onConfirm={() => {
                  handleDeletePerfil(editingPerfil.id)
                  setModalVisible(false)
                }}
                okText="Sim"
                cancelText="Não"
              >
                <Button danger icon={<DeleteOutlined />}>
                  Excluir
                </Button>
              </Popconfirm>
            )}
            <div style={{ marginLeft: 'auto' }}>
              <Button onClick={() => setModalVisible(false)} style={{ marginRight: 8 }}>
                Cancelar
              </Button>
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={saving}>
                Salvar
              </Button>
            </div>
          </div>
        </Form>
      </Modal>
    </div>
  )
}

export default Configuracoes
