import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { useAuth } from '../context/AuthContext'

export default function RegisterPage() {
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (password.length < 8) { setError('パスワードは8文字以上にしてください。'); return }
    setError('')
    setLoading(true)
    try {
      await register({ email, username, password })
      navigate('/')
    } catch (err: unknown) {
      const msg = axios.isAxiosError(err) ? err.response?.data?.detail : undefined
      setError(msg ?? '登録に失敗しました。')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-box">
        <h2>新規登録</h2>
        {error && <div className="error-msg" style={{ marginBottom: 14 }}>{error}</div>}
        <form onSubmit={handleSubmit} className="form-grid">
          <label>
            ユーザー名
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </label>
          <label>
            メールアドレス
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </label>
          <label>
            パスワード（8文字以上）
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? '登録中...' : '登録'}
          </button>
        </form>
        <div className="auth-footer">
          既にアカウントをお持ちの方は <Link to="/login">ログイン</Link>
        </div>
      </div>
    </div>
  )
}
