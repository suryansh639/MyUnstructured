import { API_ENDPOINTS } from './aws-config'

export class ApiClient {
  private token: string | null = null

  setToken(token: string) {
    this.token = token
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token)
    }
  }

  getToken(): string | null {
    if (!this.token && typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token')
    }
    return this.token
  }

  async register(email: string, password: string, name: string) {
    const response = await fetch(API_ENDPOINTS.register, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, name }),
    })
    return response.json()
  }

  async processDocument(file: File) {
    const token = this.getToken()
    if (!token) throw new Error('Not authenticated')

    const fileBuffer = await file.arrayBuffer()
    const base64File = Buffer.from(fileBuffer).toString('base64')

    const response = await fetch(API_ENDPOINTS.process, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        file: base64File,
        filename: file.name,
        output_format: 'json',
      }),
    })
    return response.json()
  }

  async getCredits() {
    const token = this.getToken()
    if (!token) throw new Error('Not authenticated')

    const response = await fetch(API_ENDPOINTS.credits, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })
    return response.json()
  }
}

export const apiClient = new ApiClient()
