import { useAuth } from '../context/AuthContext'

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth()
  return (
    <div className="container">
      <header className="app-header">
        <span className="brand">Paper Notes</span>
        <div className="user-info">
          <span>{user?.username}</span>
          <button className="btn-ghost btn-sm" onClick={logout}>ログアウト</button>
        </div>
      </header>
      {children}
    </div>
  )
}
