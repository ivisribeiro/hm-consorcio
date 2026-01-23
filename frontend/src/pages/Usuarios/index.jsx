import { useState, useEffect } from 'react'
import { Table, Button, Input, Space, Card, Tag, message, Popconfirm, Modal, Form, Select } from 'antd'
import { PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { usuariosApi } from '../../api/usuarios'
import { unidadesApi } from '../../api/unidades'

const perfilOptions = [
  { value: 'admin', label: 'Administrador' },
  { value: 'gerente', label: 'Gerente' },
  { value: 'representante', label: 'Representante' },
  { value: 'consultor', label: 'Consultor' },
]

const perfilColors = {
  admin: 'red',
  gerente: 'blue',
  representante: 'green',
  consultor: 'orange',
}

const UsuariosList = () => {
  const [usuarios, setUsuarios] = useState([])
  const [unidades, setUnidades] = useState([])
  const [loading, setLoading] = useState(false)
  const [search, setSearch] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [editingUser, setEditingUser] = useState(null)
  const [form] = Form.useForm()

  const fetchUsuarios = async (searchTerm = '') => {
    setLoading(true)
    try {
      const data = await usuariosApi.list({ search: searchTerm || undefined })
      setUsuarios(data)
    } catch (error) {
      message.error('Erro ao carregar usuários')
    } finally {
      setLoading(false)
    }
  }

  const fetchUnidades = async () => {
    try {
      const data = await unidadesApi.list()
      setUnidades(data)
    } catch (error) {
      console.error('Erro ao carregar unidades:', error)
    }
  }

  useEffect(() => {
    fetchUsuarios()
    fetchUnidades()
  }, [])

  const handleSearch = () => {
    fetchUsuarios(search)
  }

  const handleDelete = async (id) => {
    try {
      await usuariosApi.delete(id)
      message.success('Usuário desativado com sucesso')
      fetchUsuarios(search)
    } catch (error) {
      message.error('Erro ao desativar usuário')
    }
  }

  const handleOpenModal = (usuario = null) => {
    setEditingUser(usuario)
    if (usuario) {
      form.setFieldsValue(usuario)
    } else {
      form.resetFields()
    }
    setModalOpen(true)
  }

  const handleCloseModal = () => {
    setModalOpen(false)
    setEditingUser(null)
    form.resetFields()
  }

  const handleSubmit = async (values) => {
    try {
      if (editingUser) {
        await usuariosApi.update(editingUser.id, values)
        message.success('Usuário atualizado com sucesso')
      } else {
        await usuariosApi.create(values)
        message.success('Usuário criado com sucesso')
      }
      handleCloseModal()
      fetchUsuarios(search)
    } catch (error) {
      message.error(error.response?.data?.detail || 'Erro ao salvar usuário')
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
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: 'Perfil',
      dataIndex: 'perfil',
      key: 'perfil',
      render: (perfil) => (
        <Tag color={perfilColors[perfil]}>
          {perfilOptions.find(p => p.value === perfil)?.label || perfil}
        </Tag>
      ),
    },
    {
      title: 'Unidade',
      dataIndex: 'unidade_id',
      key: 'unidade_id',
      render: (id) => unidades.find(u => u.id === id)?.nome || '-',
    },
    {
      title: 'Status',
      dataIndex: 'ativo',
      key: 'ativo',
      render: (ativo) => (
        <Tag color={ativo ? 'green' : 'red'}>
          {ativo ? 'Ativo' : 'Inativo'}
        </Tag>
      ),
    },
    {
      title: 'Ações',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleOpenModal(record)}
          />
          <Popconfirm
            title="Desativar usuário?"
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
        title="Usuários"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => handleOpenModal()}
          >
            Novo Usuário
          </Button>
        }
      >
        <Space style={{ marginBottom: 16 }}>
          <Input
            placeholder="Buscar por nome ou email"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onPressEnter={handleSearch}
            style={{ width: 300 }}
          />
          <Button icon={<SearchOutlined />} onClick={handleSearch}>
            Buscar
          </Button>
        </Space>

        <Table
          columns={columns}
          dataSource={usuarios}
          rowKey="id"
          loading={loading}
        />
      </Card>

      <Modal
        title={editingUser ? 'Editar Usuário' : 'Novo Usuário'}
        open={modalOpen}
        onCancel={handleCloseModal}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="nome"
            label="Nome"
            rules={[{ required: true, message: 'Informe o nome' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Informe o email' },
              { type: 'email', message: 'Email inválido' },
            ]}
          >
            <Input />
          </Form.Item>

          {!editingUser && (
            <Form.Item
              name="senha"
              label="Senha"
              rules={[{ required: true, message: 'Informe a senha' }]}
            >
              <Input.Password />
            </Form.Item>
          )}

          <Form.Item
            name="perfil"
            label="Perfil"
            rules={[{ required: true, message: 'Selecione o perfil' }]}
          >
            <Select options={perfilOptions} />
          </Form.Item>

          <Form.Item
            name="unidade_id"
            label="Unidade"
            rules={[{ required: true, message: 'Selecione a unidade' }]}
          >
            <Select
              options={unidades.map(u => ({ value: u.id, label: u.nome }))}
            />
          </Form.Item>

          <Form.Item
            name="telefone"
            label="Telefone"
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="cpf"
            label="CPF"
          >
            <Input />
          </Form.Item>

          {editingUser && (
            <Form.Item
              name="ativo"
              label="Status"
            >
              <Select
                options={[
                  { value: true, label: 'Ativo' },
                  { value: false, label: 'Inativo' },
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

export default UsuariosList
