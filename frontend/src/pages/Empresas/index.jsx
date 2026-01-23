import { useState, useEffect } from 'react'
import { Table, Button, Space, Card, Tag, message, Popconfirm, Modal, Form, Input, Select } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { empresasApi } from '../../api/empresas'

const estados = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG',
  'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
]

const EmpresasList = () => {
  const [empresas, setEmpresas] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingEmpresa, setEditingEmpresa] = useState(null)
  const [form] = Form.useForm()

  const fetchEmpresas = async () => {
    setLoading(true)
    try {
      const data = await empresasApi.list()
      setEmpresas(data)
    } catch (error) {
      message.error('Erro ao carregar empresas')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchEmpresas()
  }, [])

  const handleDelete = async (id) => {
    try {
      await empresasApi.delete(id)
      message.success('Empresa desativada com sucesso')
      fetchEmpresas()
    } catch (error) {
      message.error('Erro ao desativar empresa')
    }
  }

  const handleOpenModal = (empresa = null) => {
    setEditingEmpresa(empresa)
    if (empresa) {
      form.setFieldsValue(empresa)
    } else {
      form.resetFields()
    }
    setModalOpen(true)
  }

  const handleCloseModal = () => {
    setModalOpen(false)
    setEditingEmpresa(null)
    form.resetFields()
  }

  const handleSubmit = async (values) => {
    try {
      if (editingEmpresa) {
        await empresasApi.update(editingEmpresa.id, values)
        message.success('Empresa atualizada com sucesso')
      } else {
        await empresasApi.create(values)
        message.success('Empresa criada com sucesso')
      }
      handleCloseModal()
      fetchEmpresas()
    } catch (error) {
      message.error(error.response?.data?.detail || 'Erro ao salvar empresa')
    }
  }

  const columns = [
    {
      title: 'Razão Social',
      dataIndex: 'razao_social',
      key: 'razao_social',
      sorter: (a, b) => a.razao_social.localeCompare(b.razao_social),
    },
    {
      title: 'Nome Fantasia',
      dataIndex: 'nome_fantasia',
      key: 'nome_fantasia',
    },
    {
      title: 'CNPJ',
      dataIndex: 'cnpj',
      key: 'cnpj',
    },
    {
      title: 'Cidade/UF',
      key: 'cidade',
      render: (_, record) => `${record.cidade || '-'}/${record.estado || '-'}`,
    },
    {
      title: 'Telefone',
      dataIndex: 'telefone',
      key: 'telefone',
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
      width: 100,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleOpenModal(record)}
          />
          <Popconfirm
            title="Desativar empresa?"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button type="link" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Card
        title="Empresas"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => handleOpenModal()}
          >
            Nova Empresa
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={empresas}
          rowKey="id"
          loading={loading}
        />
      </Card>

      <Modal
        title={editingEmpresa ? 'Editar Empresa' : 'Nova Empresa'}
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
            name="razao_social"
            label="Razão Social"
            rules={[{ required: true, message: 'Informe a razão social' }]}
          >
            <Input />
          </Form.Item>

          <Space style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="nome_fantasia"
              label="Nome Fantasia"
              style={{ flex: 1 }}
            >
              <Input />
            </Form.Item>

            <Form.Item
              name="cnpj"
              label="CNPJ"
              rules={[{ required: true, message: 'Informe o CNPJ' }]}
              style={{ width: 200 }}
            >
              <Input />
            </Form.Item>
          </Space>

          <Form.Item
            name="endereco"
            label="Endereço"
          >
            <Input />
          </Form.Item>

          <Space style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="cidade"
              label="Cidade"
              style={{ flex: 1 }}
            >
              <Input />
            </Form.Item>

            <Form.Item
              name="estado"
              label="Estado"
              style={{ width: 100 }}
            >
              <Select
                showSearch
                options={estados.map(e => ({ value: e, label: e }))}
              />
            </Form.Item>

            <Form.Item
              name="cep"
              label="CEP"
              style={{ width: 120 }}
            >
              <Input />
            </Form.Item>
          </Space>

          <Space style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="telefone"
              label="Telefone"
              style={{ flex: 1 }}
            >
              <Input />
            </Form.Item>

            <Form.Item
              name="email"
              label="Email"
              rules={[{ type: 'email', message: 'Email inválido' }]}
              style={{ flex: 1 }}
            >
              <Input />
            </Form.Item>
          </Space>

          {editingEmpresa && (
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

export default EmpresasList
