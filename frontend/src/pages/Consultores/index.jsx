import { useState, useEffect } from 'react'
import { Table, Button, Space, Card, Tag, message, Popconfirm, Modal, Form, Input, Select } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { consultoresApi } from '../../api/consultores'
import { representantesApi } from '../../api/representantes'
import { getErrorMessage } from '../../utils/errorHandler'

const ConsultoresList = () => {
  const [consultores, setConsultores] = useState([])
  const [representantes, setRepresentantes] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingConsultor, setEditingConsultor] = useState(null)
  const [form] = Form.useForm()

  const fetchConsultores = async () => {
    setLoading(true)
    try {
      const data = await consultoresApi.list()
      setConsultores(data)
    } catch (error) {
      message.error('Erro ao carregar consultores')
    } finally {
      setLoading(false)
    }
  }

  const fetchRepresentantes = async () => {
    try {
      const data = await representantesApi.list()
      setRepresentantes(data)
    } catch (error) {
      message.error('Erro ao carregar representantes')
    }
  }

  useEffect(() => {
    fetchConsultores()
    fetchRepresentantes()
  }, [])

  const handleDelete = async (id) => {
    try {
      await consultoresApi.delete(id)
      message.success('Consultor desativado com sucesso')
      fetchConsultores()
    } catch (error) {
      message.error('Erro ao desativar consultor')
    }
  }

  const handleOpenModal = (consultor = null) => {
    setEditingConsultor(consultor)
    if (consultor) {
      form.setFieldsValue(consultor)
    } else {
      form.resetFields()
    }
    setModalOpen(true)
  }

  const handleCloseModal = () => {
    setModalOpen(false)
    setEditingConsultor(null)
    form.resetFields()
  }

  const handleSubmit = async (values) => {
    try {
      if (editingConsultor) {
        await consultoresApi.update(editingConsultor.id, values)
        message.success('Consultor atualizado com sucesso')
      } else {
        await consultoresApi.create(values)
        message.success('Consultor criado com sucesso')
      }
      handleCloseModal()
      fetchConsultores()
    } catch (error) {
      message.error(getErrorMessage(error, 'Erro ao salvar consultor'))
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
      title: 'CPF',
      dataIndex: 'cpf',
      key: 'cpf',
      width: 140,
    },
    {
      title: 'Representante',
      key: 'representante',
      render: (_, record) => record.representante?.nome || '-',
    },
    {
      title: 'CNPJ (Representante)',
      key: 'cnpj',
      render: (_, record) => record.representante?.cnpj || '-',
      width: 160,
    },
    {
      title: 'Telefone',
      dataIndex: 'telefone',
      key: 'telefone',
      width: 140,
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      ellipsis: true,
    },
    {
      title: 'Status',
      dataIndex: 'ativo',
      key: 'ativo',
      width: 100,
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
          <Popconfirm
            title="Desativar consultor?"
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
        title="Consultores"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => handleOpenModal()}
          >
            Novo Consultor
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={consultores}
          rowKey="id"
          loading={loading}
          scroll={{ x: 900 }}
        />
      </Card>

      <Modal
        title={editingConsultor ? 'Editar Consultor' : 'Novo Consultor'}
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
            name="representante_id"
            label="Representante"
            rules={[{ required: true, message: 'Selecione o representante' }]}
          >
            <Select
              showSearch
              placeholder="Selecione o representante"
              optionFilterProp="children"
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={representantes.map(r => ({
                value: r.id,
                label: `${r.nome} - ${r.cnpj}`
              }))}
            />
          </Form.Item>

          <Space style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="nome"
              label="Nome Completo"
              rules={[{ required: true, message: 'Informe o nome' }]}
              style={{ flex: 1 }}
            >
              <Input />
            </Form.Item>

            <Form.Item
              name="cpf"
              label="CPF"
              rules={[{ required: true, message: 'Informe o CPF' }]}
              style={{ width: 160 }}
            >
              <Input placeholder="000.000.000-00" />
            </Form.Item>
          </Space>

          <Space style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="telefone"
              label="Telefone"
              rules={[{ required: true, message: 'Informe o telefone' }]}
              style={{ flex: 1 }}
            >
              <Input placeholder="(00) 00000-0000" />
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

          {editingConsultor && (
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

export default ConsultoresList
