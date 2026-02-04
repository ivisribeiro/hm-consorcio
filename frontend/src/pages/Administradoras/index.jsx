import { useState, useEffect } from 'react'
import { Table, Button, Space, Card, Tag, message, Modal, Form, Input, Select } from 'antd'
import { PlusOutlined, EditOutlined } from '@ant-design/icons'
import { administradorasApi } from '../../api/beneficios'
import { getErrorMessage } from '../../utils/errorHandler'

const estados = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG',
  'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
]

const AdministradorasList = () => {
  const [administradoras, setAdministradoras] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingAdmin, setEditingAdmin] = useState(null)
  const [form] = Form.useForm()

  const fetchAdministradoras = async () => {
    setLoading(true)
    try {
      const data = await administradorasApi.list()
      setAdministradoras(data)
    } catch (error) {
      message.error('Erro ao carregar administradoras')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAdministradoras()
  }, [])

  const handleOpenModal = (admin = null) => {
    setEditingAdmin(admin)
    if (admin) {
      form.setFieldsValue(admin)
    } else {
      form.resetFields()
    }
    setModalOpen(true)
  }

  const handleCloseModal = () => {
    setModalOpen(false)
    setEditingAdmin(null)
    form.resetFields()
  }

  const handleSubmit = async (values) => {
    try {
      if (editingAdmin) {
        await administradorasApi.update(editingAdmin.id, values)
        message.success('Administradora atualizada com sucesso')
      } else {
        await administradorasApi.create(values)
        message.success('Administradora criada com sucesso')
      }
      handleCloseModal()
      fetchAdministradoras()
    } catch (error) {
      message.error(getErrorMessage(error, 'Erro ao salvar administradora'))
    }
  }

  const columns = [
    {
      title: 'Nome',
      dataIndex: 'nome',
      key: 'nome',
      sorter: (a, b) => a.nome.localeCompare(b.nome),
    },
    {
      title: 'CNPJ',
      dataIndex: 'cnpj',
      key: 'cnpj',
    },
    {
      title: 'Cidade/UF',
      key: 'cidade',
      render: (_, record) =>
        record.cidade ? `${record.cidade}/${record.estado || '-'}` : '-',
    },
    {
      title: 'Telefone',
      dataIndex: 'telefone',
      key: 'telefone',
      render: (val) => val || '-',
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      render: (val) => val || '-',
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
        title="Administradoras de Consórcio"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => handleOpenModal()}
          >
            Nova Administradora
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={administradoras}
          rowKey="id"
          loading={loading}
        />
      </Card>

      <Modal
        title={editingAdmin ? 'Editar Administradora' : 'Nova Administradora'}
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
          <Space style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="nome"
              label="Nome"
              rules={[{ required: true, message: 'Informe o nome' }]}
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
                allowClear
                options={estados.map(e => ({ value: e, label: e }))}
              />
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

          <Form.Item
            name="site"
            label="Website"
          >
            <Input placeholder="https://" />
          </Form.Item>

          <Space style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="contato_nome"
              label="Nome do Contato"
              style={{ flex: 1 }}
            >
              <Input />
            </Form.Item>

            <Form.Item
              name="contato_telefone"
              label="Telefone do Contato"
              style={{ flex: 1 }}
            >
              <Input />
            </Form.Item>
          </Space>

          {editingAdmin && (
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

export default AdministradorasList
