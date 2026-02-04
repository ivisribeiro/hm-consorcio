import { useState, useEffect } from 'react'
import { Table, Button, Space, Card, Tag, message, Popconfirm, Modal, Form, Input, ColorPicker } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { perfisApi } from '../../api/perfis'

const PerfisList = () => {
  const [perfis, setPerfis] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingPerfil, setEditingPerfil] = useState(null)
  const [form] = Form.useForm()

  const fetchPerfis = async () => {
    setLoading(true)
    try {
      const data = await perfisApi.list()
      setPerfis(data)
    } catch (error) {
      message.error('Erro ao carregar perfis')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPerfis()
  }, [])

  const handleDelete = async (id) => {
    try {
      await perfisApi.delete(id)
      message.success('Perfil excluído com sucesso')
      fetchPerfis()
    } catch (error) {
      message.error(error.response?.data?.detail || 'Erro ao excluir perfil')
    }
  }

  const handleOpenModal = (perfil = null) => {
    setEditingPerfil(perfil)
    if (perfil) {
      form.setFieldsValue({
        ...perfil,
        cor: perfil.cor
      })
    } else {
      form.resetFields()
      form.setFieldsValue({ cor: '#1890ff' })
    }
    setModalOpen(true)
  }

  const handleCloseModal = () => {
    setModalOpen(false)
    setEditingPerfil(null)
    form.resetFields()
  }

  const handleSubmit = async (values) => {
    try {
      const data = {
        ...values,
        cor: typeof values.cor === 'string' ? values.cor : values.cor?.toHexString?.() || '#1890ff'
      }

      if (editingPerfil) {
        await perfisApi.update(editingPerfil.id, data)
        message.success('Perfil atualizado com sucesso')
      } else {
        await perfisApi.create(data)
        message.success('Perfil criado com sucesso')
      }
      handleCloseModal()
      fetchPerfis()
    } catch (error) {
      message.error(error.response?.data?.detail || 'Erro ao salvar perfil')
    }
  }

  const columns = [
    {
      title: 'Código',
      dataIndex: 'codigo',
      key: 'codigo',
      width: 120,
    },
    {
      title: 'Nome',
      dataIndex: 'nome',
      key: 'nome',
      sorter: (a, b) => a.nome.localeCompare(b.nome),
    },
    {
      title: 'Descrição',
      dataIndex: 'descricao',
      key: 'descricao',
    },
    {
      title: 'Cor',
      dataIndex: 'cor',
      key: 'cor',
      width: 80,
      render: (cor) => (
        <div style={{
          width: 24,
          height: 24,
          backgroundColor: cor,
          borderRadius: 4,
          border: '1px solid #d9d9d9'
        }} />
      ),
    },
    {
      title: 'Sistema',
      dataIndex: 'is_system',
      key: 'is_system',
      width: 100,
      render: (isSystem) => (
        <Tag color={isSystem ? 'red' : 'default'}>
          {isSystem ? 'Sistema' : 'Custom'}
        </Tag>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'ativo',
      key: 'ativo',
      width: 80,
      render: (ativo) => (
        <Tag color={ativo ? 'green' : 'red'}>
          {ativo ? 'Ativo' : 'Inativo'}
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
          {!record.is_system && (
            <Popconfirm
              title="Excluir perfil?"
              description="Esta ação não pode ser desfeita."
              onConfirm={() => handleDelete(record.id)}
            >
              <Button type="link" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Card
        title="Perfis de Usuário"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => handleOpenModal()}
          >
            Novo Perfil
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={perfis}
          rowKey="id"
          loading={loading}
        />
      </Card>

      <Modal
        title={editingPerfil ? 'Editar Perfil' : 'Novo Perfil'}
        open={modalOpen}
        onCancel={handleCloseModal}
        footer={null}
        width={500}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="codigo"
            label="Código"
            rules={[{ required: true, message: 'Informe o código' }]}
          >
            <Input placeholder="Ex: supervisor" disabled={editingPerfil?.is_system} />
          </Form.Item>

          <Form.Item
            name="nome"
            label="Nome"
            rules={[{ required: true, message: 'Informe o nome' }]}
          >
            <Input placeholder="Ex: Supervisor" />
          </Form.Item>

          <Form.Item
            name="descricao"
            label="Descrição"
          >
            <Input.TextArea rows={2} placeholder="Descrição do perfil..." />
          </Form.Item>

          <Form.Item
            name="cor"
            label="Cor"
            rules={[{ required: true, message: 'Selecione uma cor' }]}
          >
            <ColorPicker format="hex" />
          </Form.Item>

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

export default PerfisList
