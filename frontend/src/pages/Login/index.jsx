import { useState } from 'react'
import { Form, Input, Button, Card } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useAuth } from '../../contexts/AuthContext'

const Login = () => {
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()

  const onFinish = async (values) => {
    setLoading(true)
    await login(values.email, values.senha)
    setLoading(false)
  }

  return (
    <div className="login-container">
      <Card className="login-card" bordered={false}>
        <div className="logo-container" style={{ textAlign: 'center', marginBottom: 24 }}>
          <img
            src="/images/logo-white-bg.jpg"
            alt="HM Capital"
            style={{ maxWidth: '200px', height: 'auto', marginBottom: 16 }}
          />
          <p style={{ color: '#666', margin: 0 }}>Sistema de Gestao de Consorcios</p>
        </div>

        <Form
          name="login"
          onFinish={onFinish}
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="email"
            rules={[
              { required: true, message: 'Por favor, informe seu email!' },
              { type: 'email', message: 'Email inválido!' },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Email"
              autoComplete="email"
            />
          </Form.Item>

          <Form.Item
            name="senha"
            rules={[
              { required: true, message: 'Por favor, informe sua senha!' },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Senha"
              autoComplete="current-password"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
            >
              Entrar
            </Button>
          </Form.Item>
        </Form>

      </Card>
    </div>
  )
}

export default Login
