import { useState, useEffect } from 'react'
import { Table, Button, Space, Card, Tag, message, Popconfirm, Modal, Form, Input, Select } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { unidadesApi } from '../../api/unidades'

const estados = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG',
  'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
]

const UnidadesList = () => {
  const [unidades, setUnidades] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingUnidade, setEditingUnidade] = useState(null)
  const [form] = Form.useForm()

  const fetchUnidades = async () => {
    setLoading(true)
    try {
      const data = await unidadesApi.list()
      setUnidades(data)
    } catch (error) {
      message.error('Erro ao carregar unidades')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUnidades()
  }, [])

  const handleDelete = async (id) => {
    try {
      await unidadesApi.delete(id)
      message.success('Unidade desativada com sucesso')
      fetchUnidades()
    } catch (error) {
      message.error('Erro ao desativar unidade')
    }
  }

  const handleOpenModal = (unidade = null) => {
    setEditingUnidade(unidade)
    if (unidade) {
      form.setFieldsValue(unidade)
    } else {
      form.resetFields()
    }
    setModalOpen(true)
  }

  const handleCloseModal = () => {
    setModalOpen(false)
    setEditingUnidade(null)
    form.resetFields()
  }

  const handleSubmit = async (values) => {
    try {
      if (editingUnidade) {
        await unidadesApi.update(editingUnidade.id, values)
        message.success('Unidade atualizada com sucesso')
      } else {
        await unidadesApi.create(values)
        message.success('Unidade criada com sucesso')
      }
      handleCloseModal()
      fetchUnidades()
    } catch (error) {
      message.error(error.response?.data?.detail || 'Erro ao salvar unidade')
    }
  }

  const columns = [
    {
      title: 'Código',
      dataIndex: 'codigo',
      key: 'codigo',
      width: 100,
    },
    {
      title: 'Nome',
      dataIndex: 'nome',
      key: 'nome',
      sorter: (a, b) => a.nome.localeCompare(b.nome),
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
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
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
            title="Desativar unidade?"
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
        title="Unidades"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => handleOpenModal()}
          >
            Nova Unidade
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={unidades}
          rowKey="id"
          loading={loading}
        />
      </Card>

      <Modal
        title={editingUnidade ? 'Editar Unidade' : 'Nova Unidade'}
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
              name="codigo"
              label="Código"
              rules={[{ required: true, message: 'Informe o código' }]}
              style={{ width: 150 }}
            >
              <Input />
            </Form.Item>

            <Form.Item
              name="nome"
              label="Nome"
              rules={[{ required: true, message: 'Informe o nome' }]}
              style={{ flex: 1 }}
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

          {editingUnidade && (
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

export default UnidadesList
