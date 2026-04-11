import type { LoginRequest, RegisterRequest, TokenResponse, UserOut } from '../types/auth'
import client from './client'

export async function register(data: RegisterRequest): Promise<UserOut> {
  const res = await client.post<UserOut>('/auth/register', data)
  return res.data
}

export async function login(data: LoginRequest): Promise<TokenResponse> {
  const res = await client.post<TokenResponse>('/auth/login', data)
  return res.data
}

export async function getMe(): Promise<UserOut> {
  const res = await client.get<UserOut>('/auth/me')
  return res.data
}
