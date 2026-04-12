import client from './client'
import type { Transaction, TransactionCreate, TransactionUpdate, TransactionList } from './types'

export async function fetchTransactions(): Promise<TransactionList> {
  const { data } = await client.get<TransactionList>('/transactions')
  return data
}

export async function createTransaction(body: TransactionCreate): Promise<Transaction> {
  const { data } = await client.post<Transaction>('/transactions', body)
  return data
}

export async function updateTransaction(id: string, body: TransactionUpdate): Promise<Transaction> {
  const { data } = await client.patch<Transaction>(`/transactions/${id}`, body)
  return data
}

export async function deleteTransaction(id: string): Promise<void> {
  await client.delete(`/transactions/${id}`)
}
