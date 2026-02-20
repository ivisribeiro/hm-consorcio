import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Table, Button, Input, Space, Card, Tag, message, Popconfirm, Select } from 'antd'
import { PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons'
import { clientesApi } from '../../api/clientes'

const ClientesList = () => {
  const navigate = useNavigate()
  const [clientes, setClientes] = useState([])
  const [loading, setLoading] = useState(false)
  const [search, setSearch] = useState('')
  const [filtroAtivo, setFiltroAtivo] = useState('true')
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 })

  const fetchClientes = async (page = 1, searchTerm = '', ativo = filtroAtivo) => {
    setLoading(true)
    try {
      const params = {
        skip: (page - 1) * pagination.pageSize,
        limit: pagination.pageSize,
        search: searchTerm || undefined,
      }
      if (ativo !== 'todos') {
        params.ativo = ativo === 'true'
      } else {
        params.ativo = ''
      }
      const data = await clientesApi.list(params)
      setClientes(data)
      setPagination(prev => ({ ...prev, current: page, total: data.length }))
    } catch (error) {
      message.error('Erro ao carregar clientes')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchClientes()
  }, [])

  const handleSearch = () => {
    fetchClientes(1, search, filtroAtivo)
  }

  const handleFiltroAtivoChange = (value) => {
    setFiltroAtivo(value)
    fetchClientes(1, search, value)
  }

  const handleDelete = async (id) => {
    try {
      await clientesApi.delete(id)
      message.success('Cliente desativado com sucesso')
      fetchClientes(pagination.current, search)
    } catch (error) {
      message.error('Erro ao desativar cliente')
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
    },
    {
      title: 'Telefone',
      dataIndex: 'telefone',
      key: 'telefone',
    },
    {
      title: 'Cidade/UF',
      key: 'cidade',
      render: (_, record) => record.cidade ? `${record.cidade}/${record.estado}` : '-',
    },
    {
      title: 'Salário',
      dataIndex: 'salario',
      key: 'salario',
      render: (val) => val ? `R$ ${Number(val).toLocaleString('pt-BR')}` : '-',
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
            icon={<EyeOutlined />}
            onClick={() => navigate(`/clientes/${record.id}`)}
          />
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => navigate(`/clientes/${record.id}/editar`)}
          />
          <Popconfirm
            title="Desativar cliente?"
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
        title="Clientes"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate('/clientes/novo')}
          >
            Novo Cliente
          </Button>
        }
      >
        <Space style={{ marginBottom: 16 }} wrap>
          <Input
            placeholder="Buscar por nome, CPF ou telefone"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onPressEnter={handleSearch}
            style={{ width: 300 }}
          />
          <Select
            value={filtroAtivo}
            onChange={handleFiltroAtivoChange}
            style={{ width: 140 }}
            options={[
              { value: 'true', label: 'Ativos' },
              { value: 'false', label: 'Inativos' },
              { value: 'todos', label: 'Todos' },
            ]}
          />
          <Button icon={<SearchOutlined />} onClick={handleSearch}>
            Buscar
          </Button>
        </Space>

        <Table
          columns={columns}
          dataSource={clientes}
          rowKey="id"
          loading={loading}
          pagination={{
            ...pagination,
            onChange: (page) => fetchClientes(page, search),
          }}
        />
      </Card>
    </div>
  )
}

export default ClientesList
