import { supabase } from './supabase'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

async function getAuthHeader(): Promise<Record<string, string>> {
  const { data: { session } } = await supabase.auth.getSession()
  
  if (!session?.access_token) {
    return {}
  }
  
  return {
    'Authorization': `Bearer ${session.access_token}`,
    'Content-Type': 'application/json',
  }
}

export interface CheckoutSessionRequest {
  plan: 'starter' | 'pro'
  billingCycle: 'monthly' | 'yearly'
  successUrl: string
  cancelUrl: string
}

export interface CheckoutSessionResponse {
  session_id: string
  url: string
}

export interface SubscriptionStatus {
  id?: string
  status: 'active' | 'inactive' | 'canceled' | 'past_due'
  plan: 'free' | 'starter' | 'pro'
  current_period_end?: number
  cancel_at_period_end?: boolean
  stripe_connected: boolean
}

export interface PortalSessionResponse {
  url: string
}

export async function createCheckoutSession(data: CheckoutSessionRequest): Promise<CheckoutSessionResponse> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/stripe/checkout`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      plan: data.plan,
      billing_cycle: data.billingCycle,
      success_url: data.successUrl,
      cancel_url: data.cancelUrl,
    }),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create checkout session')
  }
  
  return response.json()
}

export async function getSubscriptionStatus(): Promise<SubscriptionStatus> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/stripe/subscription`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch subscription status')
  }
  
  return response.json()
}

export async function createPortalSession(): Promise<PortalSessionResponse> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/stripe/portal`, {
    method: 'POST',
    headers,
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create portal session')
  }
  
  return response.json()
}

export async function getStripeConfig(): Promise<{ is_configured: boolean; test_mode: boolean }> {
  const response = await fetch(`${API_URL}/stripe/config`)
  
  if (!response.ok) {
    return { is_configured: false, test_mode: true }
  }
  
  return response.json()
}
