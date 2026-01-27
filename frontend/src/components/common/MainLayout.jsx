import { useState } from 'react'
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

const menuItems = [
  {
    key: '/',
    icon: <DashboardOutlined />,
    label: 'Dashboard',
  },
  {
    key: '/clientes',
    icon: <TeamOutlined />,
    label: 'Clientes',
  },
  {
    key: '/beneficios',
    icon: <GiftOutlined />,
    label: 'Benefícios',
  },
  {
    key: '/relatorios',
    icon: <FilePdfOutlined />,
    label: 'Relatórios',
  },
  {
    key: 'cadastros',
    icon: <SettingOutlined />,
    label: 'Cadastros',
    children: [
      {
        key: '/usuarios',
        icon: <UserOutlined />,
        label: 'Usuários',
      },
      {
        key: '/unidades',
        icon: <ApartmentOutlined />,
        label: 'Unidades',
      },
      {
        key: '/empresas',
        icon: <ShopOutlined />,
        label: 'Empresas',
      },
      {
        key: '/representantes',
        icon: <IdcardOutlined />,
        label: 'Representantes',
      },
      {
        key: '/consultores',
        icon: <SolutionOutlined />,
        label: 'Consultores',
      },
      {
        key: '/tabelas-credito',
        icon: <TableOutlined />,
        label: 'Tabelas de Crédito',
      },
      {
        key: '/administradoras',
        icon: <BankOutlined />,
        label: 'Administradoras',
      },
    ],
  },
  {
    key: '/configuracoes',
    icon: <SafetyCertificateOutlined />,
    label: 'Configurações',
  },
]

const MainLayout = () => {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuth()

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
          items={menuItems}
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
