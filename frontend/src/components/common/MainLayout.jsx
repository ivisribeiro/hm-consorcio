import { useState, useMemo } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Avatar, Dropdown, Space, Typography } from 'antd'
import {
  DashboardOutlined,
  UserOutlined,
  FileTextOutlined,
  SettingOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  TeamOutlined,
  GiftOutlined,
  BankOutlined,
  ShopOutlined,
  TableOutlined,
  SafetyCertificateOutlined,
  ApartmentOutlined,
  FilePdfOutlined,
  IdcardOutlined,
  SolutionOutlined,
} from '@ant-design/icons'
import { useAuth } from '../../contexts/AuthContext'

const { Header, Sider, Content, Footer } = Layout
const { Text } = Typography

// Definição dos itens de menu com permissões requeridas
// Códigos de permissão seguem o padrão do backend: modulo.acao
const allMenuItems = [
  {
    key: '/',
    icon: <DashboardOutlined />,
    label: 'Dashboard',
    permission: null, // Todos podem ver
  },
  {
    key: '/clientes',
    icon: <TeamOutlined />,
    label: 'Clientes',
    permission: 'clientes.visualizar',
  },
  {
    key: '/beneficios',
    icon: <GiftOutlined />,
    label: 'Benefícios',
    permission: 'beneficios.visualizar',
  },
  {
    key: '/relatorios',
    icon: <FilePdfOutlined />,
    label: 'Relatórios',
    permission: 'relatorios.ficha', // Qualquer permissão de relatórios
  },
  {
    key: 'cadastros',
    icon: <SettingOutlined />,
    label: 'Cadastros',
    permission: null, // Visível se tiver pelo menos um filho
    children: [
      {
        key: '/usuarios',
        icon: <UserOutlined />,
        label: 'Usuários',
        permission: 'cadastros.usuarios',
      },
      {
        key: '/unidades',
        icon: <ApartmentOutlined />,
        label: 'Unidades',
        permission: 'cadastros.unidades',
      },
      {
        key: '/empresas',
        icon: <ShopOutlined />,
        label: 'Empresas',
        permission: 'cadastros.empresas',
      },
      {
        key: '/representantes',
        icon: <IdcardOutlined />,
        label: 'Representantes',
        permission: 'cadastros.representantes',
      },
      {
        key: '/consultores',
        icon: <SolutionOutlined />,
        label: 'Consultores',
        permission: 'cadastros.consultores',
      },
      {
        key: '/tabelas-credito',
        icon: <TableOutlined />,
        label: 'Tabelas de Crédito',
        permission: 'cadastros.tabelas_credito',
      },
      {
        key: '/administradoras',
        icon: <BankOutlined />,
        label: 'Administradoras',
        permission: 'cadastros.administradoras',
      },
      {
        key: '/perfis',
        icon: <SafetyCertificateOutlined />,
        label: 'Perfis',
        permission: 'configuracoes.perfis',
      },
    ],
  },
  {
    key: '/configuracoes',
    icon: <SettingOutlined />,
    label: 'Configurações',
    permission: 'configuracoes.sistema',
  },
]

const MainLayout = () => {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout, hasPermission } = useAuth()

  // Filtra itens do menu baseado nas permissões do usuário
  const filteredMenuItems = useMemo(() => {
    const filterItems = (items) => {
      return items
        .filter(item => {
          // Se não tem permissão definida, sempre mostra
          if (!item.permission) return true
          // Verifica se tem a permissão
          return hasPermission(item.permission)
        })
        .map(item => {
          // Se tem filhos, filtra recursivamente
          if (item.children) {
            const filteredChildren = filterItems(item.children)
            // Só mostra o item pai se tiver pelo menos um filho visível
            if (filteredChildren.length === 0) return null
            return { ...item, children: filteredChildren }
          }
          return item
        })
        .filter(Boolean) // Remove nulls
    }
    return filterItems(allMenuItems)
  }, [hasPermission])

  const handleMenuClick = ({ key }) => {
    if (key.startsWith('/')) {
      navigate(key)
    }
  }

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Meu Perfil',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Sair',
      danger: true,
    },
  ]

  const handleUserMenuClick = ({ key }) => {
    if (key === 'logout') {
      logout()
    } else if (key === 'profile') {
      navigate('/configuracoes')
    }
  }

  return (
    <Layout className="main-layout">
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        theme="dark"
        width={240}
      >
        <div
          className={`logo ${collapsed ? 'collapsed' : ''}`}
          style={{
            height: collapsed ? '50px' : '64px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: collapsed ? '8px' : '12px 16px',
            background: '#001529',
            borderBottom: '1px solid rgba(255,255,255,0.1)',
            overflow: 'hidden'
          }}
        >
          <img
            src="/images/logo-dark-bg.jpg"
            alt="HM Capital"
            style={{
              maxWidth: collapsed ? '32px' : '180px',
              maxHeight: collapsed ? '32px' : '40px',
              width: 'auto',
              height: 'auto',
              transition: 'all 0.3s',
              borderRadius: '4px',
              objectFit: 'contain'
            }}
          />
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          defaultOpenKeys={['cadastros']}
          items={filteredMenuItems}
          onClick={handleMenuClick}
        />
      </Sider>

      <Layout className="site-layout">
        <Header style={{ background: '#fff', padding: '0 24px' }}>
          <Space style={{ width: '100%', justifyContent: 'space-between' }}>
            <span
              onClick={() => setCollapsed(!collapsed)}
              style={{ cursor: 'pointer', fontSize: 18 }}
            >
              {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            </span>

            <Dropdown
              menu={{
                items: userMenuItems,
                onClick: handleUserMenuClick,
              }}
              trigger={['click']}
            >
              <Space style={{ cursor: 'pointer' }}>
                <Avatar icon={<UserOutlined />} />
                <Text>{user?.nome}</Text>
              </Space>
            </Dropdown>
          </Space>
        </Header>

        <Content className="site-layout-content">
          <Outlet />
        </Content>

        <Footer style={{ textAlign: 'center', background: '#f0f2f5' }}>
          HM Capital - CRM Consorcios - {new Date().getFullYear()}
        </Footer>
      </Layout>
    </Layout>
  )
}

export default MainLayout
