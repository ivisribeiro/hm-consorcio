import { useState, useEffect } from 'react'
import { Table, Button, Space, Card, Tag, message, Popconfirm, Modal, Form, Input, Select, Divider } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { representantesApi } from '../../api/representantes'
import { unidadesApi } from '../../api/unidades'
import { getErrorMessage } from '../../utils/errorHandler'

const RepresentantesList = () => {
  const [representantes, setRepresentantes] = useState([])
  const [unidades, setUnidades] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingRepresentante, setEditingRepresentante] = useState(null)
  const [form] = Form.useForm()

  const fetchRepresentantes = async () => {
    setLoading(true)
    try {
      const data = await representantesApi.list()
      setRepresentantes(data)
    } catch (error) {
      message.error('Erro ao carregar representantes')
    } finally {
      setLoading(false)
    }
  }

  const fetchUnidades = async () => {
    try {
      const data = await unidadesApi.list()
      setUnidades(data)
    } catch (error) {
      message.error('Erro ao carregar unidades')
    }
  }

  useEffect(() => {
    fetchRepresentantes()
    fetchUnidades()
  }, [])

  const handleDelete = async (id) => {
    try {
      await representantesApi.delete(id)
      message.success('Representante desativado com sucesso')
      fetchRepresentantes()
    } catch (error) {
      message.error('Erro ao desativar representante')
    }
  }

  const handleOpenModal = (representante = null) => {
    setEditingRepresentante(representante)
    if (representante) {
      form.setFieldsValue(representante)
    } else {
      form.resetFields()
    }
    setModalOpen(true)
  }

  const handleCloseModal = () => {
    setModalOpen(false)
    setEditingRepresentante(null)
    form.resetFields()
  }

  const handleSubmit = async (values) => {
    try {
      if (editingRepresentante) {
        await representantesApi.update(editingRepresentante.id, values)
        message.success('Representante atualizado com sucesso')
      } else {
        await representantesApi.create(values)
        message.success('Representante criado com sucesso')
      }
      handleCloseModal()
      fetchRepresentantes()
    } catch (error) {
      message.error(getErrorMessage(error, 'Erro ao salvar representante'))
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
      title: 'CNPJ',
      dataIndex: 'cnpj',
      key: 'cnpj',
      width: 160,
    },
    {
      title: 'Razão Social',
      dataIndex: 'razao_social',
      key: 'razao_social',
      ellipsis: true,
    },
    {
      title: 'Unidade',
      key: 'unidade',
      render: (_, record) => record.unidade?.nome || '-',
    },
    {
      title: 'Telefone',
      dataIndex: 'telefone',
      key: 'telefone',
      width: 140,
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
            title="Desativar representante?"
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
        title="Representantes"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => handleOpenModal()}
          >
            Novo Representante
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={representantes}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1000 }}
        />
      </Card>

      <Modal
        title={editingRepresentante ? 'Editar Representante' : 'Novo Representante'}
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
          <Divider orientation="left" style={{ marginTop: 0 }}>Dados do Representante</Divider>

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

          <Divider orientation="left">Dados da Empresa (CNPJ)</Divider>

          <Space style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="cnpj"
              label="CNPJ"
              rules={[{ required: true, message: 'Informe o CNPJ' }]}
              style={{ width: 200 }}
            >
              <Input placeholder="00.000.000/0000-00" />
            </Form.Item>

            <Form.Item
              name="razao_social"
              label="Razão Social"
              rules={[{ required: true, message: 'Informe a razão social' }]}
              style={{ flex: 1 }}
            >
              <Input />
            </Form.Item>
          </Space>

          <Form.Item
            name="nome_fantasia"
            label="Nome Fantasia"
          >
            <Input />
          </Form.Item>

          <Divider orientation="left">Vínculo</Divider>

          <Form.Item
            name="unidade_id"
            label="Unidade"
            rules={[{ required: true, message: 'Selecione a unidade' }]}
          >
            <Select
              showSearch
              placeholder="Selecione a unidade"
              optionFilterProp="children"
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={unidades.map(u => ({
                value: u.id,
                label: `${u.codigo} - ${u.nome}`
              }))}
            />
          </Form.Item>

          {editingRepresentante && (
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

export default RepresentantesList
