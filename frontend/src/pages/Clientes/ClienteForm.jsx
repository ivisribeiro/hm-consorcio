import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Form, Input, Button, Card, Row, Col, Select, DatePicker,
  Radio, Switch, message, Spin, Divider, Collapse, Space
} from 'antd'
import { SaveOutlined, ArrowLeftOutlined, FilePdfOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { clientesApi, unidadesApi, empresasApi } from '../../api/clientes'
import { relatoriosApi } from '../../api/relatorios'
import CPFInput from '../../components/forms/CPFInput'
import CEPInput from '../../components/forms/CEPInput'
import PhoneInput from '../../components/forms/PhoneInput'
import MoneyInput from '../../components/forms/MoneyInput'

const { Option } = Select
const { TextArea } = Input

const ClienteForm = () => {
  const navigate = useNavigate()
  const { id } = useParams()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [downloadingPdf, setDownloadingPdf] = useState(false)
  const [unidades, setUnidades] = useState([])
  const [empresas, setEmpresas] = useState([])
  const [clienteNome, setClienteNome] = useState('')

  const isEdit = !!id

  useEffect(() => {
    loadOptions()
    if (isEdit) {
      loadCliente()
    }
  }, [id])

  const loadOptions = async () => {
    try {
      const [unidadesData, empresasData] = await Promise.all([
        unidadesApi.list(),
        empresasApi.list(),
      ])
      setUnidades(unidadesData)
      setEmpresas(empresasData)
    } catch (error) {
      message.error('Erro ao carregar opções')
    }
  }

  const loadCliente = async () => {
    setLoading(true)
    try {
      const data = await clientesApi.get(id)
      setClienteNome(data.nome || '')
      form.setFieldsValue({
        ...data,
        data_nascimento: data.data_nascimento ? dayjs(data.data_nascimento) : null,
        data_expedicao: data.data_expedicao ? dayjs(data.data_expedicao) : null,
        conjuge_data_nascimento: data.conjuge_data_nascimento ? dayjs(data.conjuge_data_nascimento) : null,
      })
    } catch (error) {
      message.error('Erro ao carregar cliente')
      navigate('/clientes')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadFicha = async () => {
    setDownloadingPdf(true)
    try {
      const blob = await relatoriosApi.gerarFichaAtendimento(id)
      const nomeArquivo = `ficha_${clienteNome.replace(/\s+/g, '_').toLowerCase()}_${id}.pdf`
      relatoriosApi.downloadPdf(blob, nomeArquivo)
      message.success('Ficha de Atendimento gerada com sucesso!')
    } catch (error) {
      message.error('Erro ao gerar Ficha de Atendimento')
    } finally {
      setDownloadingPdf(false)
    }
  }

  const handleAddressFound = (address) => {
    form.setFieldsValue({
      logradouro: address.logradouro,
      bairro: address.bairro,
      cidade: address.cidade,
      estado: address.estado,
    })
  }

  const onFinish = async (values) => {
    setSaving(true)
    try {
      const data = {
        ...values,
        data_nascimento: values.data_nascimento?.format('YYYY-MM-DD'),
        data_expedicao: values.data_expedicao?.format('YYYY-MM-DD'),
        conjuge_data_nascimento: values.conjuge_data_nascimento?.format('YYYY-MM-DD'),
      }

      if (isEdit) {
        await clientesApi.update(id, data)
        message.success('Cliente atualizado com sucesso!')
      } else {
        await clientesApi.create(data)
        message.success('Cliente cadastrado com sucesso!')
      }
      navigate('/clientes')
    } catch (error) {
      const errorData = error.response?.data
      if (errorData?.detail) {
        // Se detail é um array (erros de validação do Pydantic)
        if (Array.isArray(errorData.detail)) {
          const fieldErrors = errorData.detail.map(err => {
            const field = err.loc?.[1] || err.loc?.[0] || 'campo'
            const fieldNames = {
              'nome': 'Nome',
              'cpf': 'CPF',
              'telefone': 'Telefone',
              'email': 'Email',
              'unidade_id': 'Unidade',
              'data_nascimento': 'Data de Nascimento',
              'data_expedicao': 'Data de Expedição',
              'sexo': 'Sexo',
              'estado_civil': 'Estado Civil',
              'salario': 'Salário',
            }
            return `${fieldNames[field] || field}: ${err.msg}`
          })
          message.error({
            content: fieldErrors.join(' | '),
            duration: 6,
          })
        } else {
          // Se detail é uma string
          message.error(errorData.detail)
        }
      } else {
        message.error('Erro ao salvar cliente. Verifique os dados e tente novamente.')
      }
    } finally {
      setSaving(false)
    }
  }

  const collapseItems = [
    {
      key: '1',
      label: 'Dados Básicos',
      children: (
        <>
          <Row gutter={16}>
            <Col xs={24} sm={8}>
              <Form.Item name="natureza" label="Natureza" initialValue="fisica">
                <Radio.Group>
                  <Radio value="fisica">Pessoa Física</Radio>
                  <Radio value="juridica">Pessoa Jurídica</Radio>
                </Radio.Group>
              </Form.Item>
            </Col>
            <Col xs={24} sm={8}>
              <Form.Item name="unidade_id" label="Unidade" rules={[{ required: true }]}>
                <Select placeholder="Selecione">
                  {unidades.map(u => <Option key={u.id} value={u.id}>{u.nome}</Option>)}
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} sm={8}>
              <Form.Item name="empresa_id" label="Empresa">
                <Select placeholder="Selecione" allowClear>
                  {empresas.map(e => <Option key={e.id} value={e.id}>{e.nome_fantasia || e.razao_social}</Option>)}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} sm={12}>
              <Form.Item name="nome" label="Nome Completo" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
            </Col>
            <Col xs={24} sm={6}>
              <Form.Item name="cpf" label="CPF" rules={[{ required: true }]}>
                <CPFInput />
              </Form.Item>
            </Col>
            <Col xs={24} sm={6}>
              <Form.Item name="telefone" label="Telefone" rules={[{ required: true }]}>
                <PhoneInput />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} sm={6}>
              <Form.Item name="identidade" label="Identidade">
                <Input />
              </Form.Item>
            </Col>
            <Col xs={24} sm={6}>
              <Form.Item name="orgao_expedidor" label="Órgão Expedidor">
                <Input />
              </Form.Item>
            </Col>
            <Col xs={24} sm={6}>
              <Form.Item name="data_expedicao" label="Data Expedição">
                <DatePicker format="DD/MM/YYYY" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={6}>
              <Form.Item name="data_nascimento" label="Data Nascimento">
                <DatePicker format="DD/MM/YYYY" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} sm={6}>
              <Form.Item name="sexo" label="Sexo">
                <Select placeholder="Selecione" allowClear>
                  <Option value="feminino">Feminino</Option>
                  <Option value="masculino">Masculino</Option>
                  <Option value="outro">Outro</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} sm={6}>
              <Form.Item name="estado_civil" label="Estado Civil">
                <Select placeholder="Selecione" allowClear>
                  <Option value="solteiro">Solteiro(a)</Option>
                  <Option value="casado">Casado(a)</Option>
                  <Option value="divorciado">Divorciado(a)</Option>
                  <Option value="viuvo">Viúvo(a)</Option>
                  <Option value="uniao_estavel">União Estável</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} sm={6}>
              <Form.Item name="nacionalidade" label="Nacionalidade" initialValue="Brasileira">
                <Input />
              </Form.Item>
            </Col>
            <Col xs={24} sm={6}>
              <Form.Item name="naturalidade" label="Naturalidade">
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} sm={12}>
              <Form.Item name="nome_mae" label="Nome da Mãe">
                <Input />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item name="nome_pai" label="Nome do Pai">
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} sm={8}>
              <Form.Item name="telefone_secundario" label="Telefone Secundário">
                <PhoneInput />
              </Form.Item>
            </Col>
            <Col xs={24} sm={8}>
              <Form.Item name="email" label="Email">
                <Input type="email" />
              </Form.Item>
            </Col>
          </Row>
        </>
      ),
    },
    {
      key: '2',
      label: 'Cônjuge',
      children: (
        <Row gutter={16}>
          <Col xs={24} sm={10}>
            <Form.Item name="conjuge_nome" label="Nome do Cônjuge">
              <Input />
            </Form.Item>
          </Col>
          <Col xs={24} sm={7}>
            <Form.Item name="conjuge_cpf" label="CPF do Cônjuge">
              <CPFInput />
            </Form.Item>
          </Col>
          <Col xs={24} sm={7}>
            <Form.Item name="conjuge_data_nascimento" label="Data Nascimento">
              <DatePicker format="DD/MM/YYYY" style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        </Row>
      ),
    },
    {
      key: '3',
      label: 'Endereço',
      children: (
        <>
          <Row gutter={16}>
            <Col xs={24} sm={6}>
              <Form.Item name="cep" label="CEP">
                <CEPInput onAddressFound={handleAddressFound} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item name="logradouro" label="Logradouro">
                <Input />
              </Form.Item>
            </Col>
            <Col xs={24} sm={6}>
              <Form.Item name="numero" label="Número">
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} sm={6}>
              <Form.Item name="complemento" label="Complemento">
                <Input />
              </Form.Item>
            </Col>
            <Col xs={24} sm={6}>
              <Form.Item name="bairro" label="Bairro">
                <Input />
              </Form.Item>
            </Col>
            <Col xs={24} sm={6}>
              <Form.Item name="cidade" label="Cidade">
                <Input />
              </Form.Item>
            </Col>
            <Col xs={24} sm={6}>
              <Form.Item name="estado" label="UF">
                <Select placeholder="UF" allowClear>
                  {['AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO'].map(uf => (
                    <Option key={uf} value={uf}>{uf}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
        </>
      ),
    },
    {
      key: '4',
      label: 'Compromissos Financeiros',
      children: (
        <>
          {[
            { key: 'consorcio', label: 'Consórcio', hasPrazo: true },
            { key: 'emprestimo_contracheque', label: 'Empréstimo no Contracheque', hasPrazo: true },
            { key: 'emprestimo_outros', label: 'Empréstimos (Leasing, CDC, Crediário)', hasPrazo: true },
            { key: 'financiamento_estudantil', label: 'Financiamento Estudantil', hasPrazo: true },
            { key: 'financiamento_veicular', label: 'Financiamento Veicular', hasPrazo: true },
            { key: 'financiamento_habitacional', label: 'Financiamento Habitacional', hasPrazo: true },
            { key: 'aluguel', label: 'Aluguel', hasPrazo: false },
            { key: 'outras_dividas', label: 'Outras Dívidas', hasPrazo: false },
          ].map(item => (
            <Row gutter={16} key={item.key} align="middle" style={{ marginBottom: 12, padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
              <Col xs={24} sm={8}>
                <Form.Item name={`tem_${item.key}`} valuePropName="checked" initialValue={false} style={{ marginBottom: 0 }}>
                  <Switch checkedChildren="Sim" unCheckedChildren="Não" />
                </Form.Item>
                <span style={{ marginLeft: 8 }}>{item.label}</span>
              </Col>
              {item.hasPrazo && (
                <Col xs={12} sm={8}>
                  <Form.Item name={`${item.key}_prazo`} label="Prazo (meses)" style={{ marginBottom: 0 }}>
                    <Input type="number" />
                  </Form.Item>
                </Col>
              )}
              <Col xs={12} sm={item.hasPrazo ? 8 : 16}>
                <Form.Item name={`${item.key}_valor`} label="Valor Parcela (R$)" style={{ marginBottom: 0 }}>
                  <MoneyInput />
                </Form.Item>
              </Col>
            </Row>
          ))}

          <Divider />

          <Row gutter={16}>
            <Col xs={24} sm={12}>
              <Form.Item name="possui_restricao" valuePropName="checked" initialValue={false}>
                <Switch checkedChildren="Sim" unCheckedChildren="Não" /> Possui Restrição no Nome?
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item name="tentou_credito_12_meses" valuePropName="checked" initialValue={false}>
                <Switch checkedChildren="Sim" unCheckedChildren="Não" /> Tentou Obter Crédito nos Últimos 12 Meses?
              </Form.Item>
            </Col>
          </Row>
        </>
      ),
    },
    {
      key: '5',
      label: 'Dados Profissionais',
      children: (
        <Row gutter={16}>
          <Col xs={24} sm={10}>
            <Form.Item name="empresa_trabalho" label="Empresa onde Trabalha">
              <Input />
            </Form.Item>
          </Col>
          <Col xs={24} sm={6}>
            <Form.Item name="cargo" label="Cargo">
              <Input />
            </Form.Item>
          </Col>
          <Col xs={24} sm={8}>
            <Form.Item name="salario" label="Salário (R$)">
              <MoneyInput />
            </Form.Item>
          </Col>
        </Row>
      ),
    },
    {
      key: '6',
      label: 'Preferências de Crédito',
      children: (
        <Row gutter={16}>
          <Col xs={24} sm={8}>
            <Form.Item name="parcela_maxima" label="Parcela Máxima Desejada (R$)">
              <MoneyInput />
            </Form.Item>
          </Col>
          <Col xs={24} sm={8}>
            <Form.Item name="valor_carta_desejado" label="Valor da Carta Desejado (R$)">
              <MoneyInput />
            </Form.Item>
          </Col>
          <Col xs={24} sm={8}>
            <Form.Item name="taxa_inicial" label="Taxa Inicial (%)">
              <Input type="number" step="0.01" />
            </Form.Item>
          </Col>
        </Row>
      ),
    },
    {
      key: '7',
      label: 'Dados Bancários',
      children: (
        <Row gutter={16}>
          <Col xs={24} sm={6}>
            <Form.Item name="banco" label="Banco">
              <Input />
            </Form.Item>
          </Col>
          <Col xs={24} sm={6}>
            <Form.Item name="tipo_conta" label="Tipo de Conta">
              <Select placeholder="Selecione" allowClear>
                <Option value="corrente">Corrente</Option>
                <Option value="poupanca">Poupança</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col xs={12} sm={4}>
            <Form.Item name="agencia" label="Agência">
              <Input />
            </Form.Item>
          </Col>
          <Col xs={12} sm={4}>
            <Form.Item name="conta" label="Conta">
              <Input />
            </Form.Item>
          </Col>
          <Col xs={24} sm={4}>
            <Form.Item name="chave_pix" label="Chave PIX">
              <Input />
            </Form.Item>
          </Col>
        </Row>
      ),
    },
    {
      key: '8',
      label: 'Observações',
      children: (
        <Form.Item name="observacoes">
          <TextArea rows={4} placeholder="Observações sobre o cliente..." />
        </Form.Item>
      ),
    },
  ]

  if (loading) {
    return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />
  }

  return (
    <Card
      title={isEdit ? 'Editar Cliente' : 'Novo Cliente'}
      extra={
        <Space>
          {isEdit && (
            <Button
              icon={<FilePdfOutlined />}
              onClick={handleDownloadFicha}
              loading={downloadingPdf}
              type="primary"
              ghost
            >
              Ficha de Atendimento
            </Button>
          )}
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/clientes')}>
            Voltar
          </Button>
        </Space>
      }
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
        initialValues={{ natureza: 'fisica', nacionalidade: 'Brasileira' }}
      >
        <Collapse
          items={collapseItems}
          defaultActiveKey={['1', '2', '3', '4', '5', '6', '7', '8']}
          style={{ marginBottom: 24 }}
        />

        <div style={{ textAlign: 'right', marginTop: 16 }}>
          <Button type="primary" htmlType="submit" loading={saving} icon={<SaveOutlined />} size="large">
            {isEdit ? 'Atualizar' : 'Cadastrar'}
          </Button>
        </div>
      </Form>
    </Card>
  )
}

export default ClienteForm
