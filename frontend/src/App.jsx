import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './contexts/AuthContext'
import MainLayout from './components/common/MainLayout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import ClientesList from './pages/Clientes'
import ClienteForm from './pages/Clientes/ClienteForm'
import BeneficiosList from './pages/Beneficios'
import BeneficioForm from './pages/Beneficios/BeneficioForm'
import BeneficioDetail from './pages/Beneficios/BeneficioDetail'
import UsuariosList from './pages/Usuarios'
import UnidadesList from './pages/Unidades'
import EmpresasList from './pages/Empresas'
import RepresentantesList from './pages/Representantes'
import ConsultoresList from './pages/Consultores'
import TabelasCreditoList from './pages/TabelasCredito'
import AdministradorasList from './pages/Administradoras'
import Relatorios from './pages/Relatorios'
import Configuracoes from './pages/Configuracoes'
import PerfisList from './pages/Perfis'

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return <div>Carregando...</div>
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}

const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return <div>Carregando...</div>
  if (isAuthenticated) return <Navigate to="/" replace />
  return children
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />

      <Route path="/" element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
        <Route index element={<Dashboard />} />
        <Route path="dashboard" element={<Dashboard />} />

        {/* Clientes */}
        <Route path="clientes" element={<ClientesList />} />
        <Route path="clientes/novo" element={<ClienteForm />} />
        <Route path="clientes/:id" element={<ClienteForm />} />
        <Route path="clientes/:id/editar" element={<ClienteForm />} />

        {/* Benefícios */}
        <Route path="beneficios" element={<BeneficiosList />} />
        <Route path="beneficios/novo" element={<BeneficioForm />} />
        <Route path="beneficios/:id" element={<BeneficioDetail />} />

        {/* Cadastros */}
        <Route path="usuarios" element={<UsuariosList />} />
        <Route path="unidades" element={<UnidadesList />} />
        <Route path="empresas" element={<EmpresasList />} />
        <Route path="representantes" element={<RepresentantesList />} />
        <Route path="consultores" element={<ConsultoresList />} />
        <Route path="tabelas-credito" element={<TabelasCreditoList />} />
        <Route path="administradoras" element={<AdministradorasList />} />

        {/* Relatórios */}
        <Route path="relatorios" element={<Relatorios />} />

        {/* Configuracoes */}
        <Route path="configuracoes" element={<Configuracoes />} />
        <Route path="perfis" element={<PerfisList />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
