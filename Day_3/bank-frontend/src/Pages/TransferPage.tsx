import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { useSearchParams } from 'react-router-dom'
import Layout from '../Components/Layout/Layout'
import { useAuth } from '../Context/AuthContext'
import { useAccounts } from '../hooks/accounts/useAccounts'
import { formatCurrency } from '../data/accounts'
import { post } from '../api/client'
import { PageWrapper, PageTitle, PageSubtitle } from '../Components/PageHero/PageHero.styled'
import { FormGroup, Label, SubmitButton, StatusMessage, ErrorMessage } from '../Components/Form/Form.styled'
import { TransferForm, Select, AmountField, CurrencyPrefix, AmountInput } from './TransferPage.styled'

function TransferPage() {
  const { customer } = useAuth()
  const { accounts, isLoading, error: loadError, refetch } = useAccounts(customer?.user_id)
  const [searchParams] = useSearchParams()
  const initialFrom = searchParams.get('from')

  const [fromId, setFromId] = useState('')
  const [toId, setToId] = useState('')
  const [amount, setAmount] = useState('')
  const [error, setError] = useState('')
  const [submitted, setSubmitted] = useState(false)

  // Once accounts have loaded, pick a starting "From" account: the one
  // passed in the URL (e.g. from the Accounts page's Transfer button) if
  // it's valid, otherwise just the first account.
  useEffect(() => {
    if (accounts.length === 0) return
    setFromId((current) => current || initialFrom || accounts[0].account_id)
  }, [accounts, initialFrom])

  // Once "From" is known, default "To" to a different account.
  useEffect(() => {
    if (accounts.length === 0 || !fromId) return
    setToId((current) => {
      if (current && current !== fromId) return current
      const fallback = accounts.find((account) => account.account_id !== fromId)
      return fallback ? fallback.account_id : ''
    })
  }, [accounts, fromId])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitted(false)
    setError('')

    if (fromId === toId) {
      setError('From and To accounts must be different.')
      return
    }

    if (!customer) return

    try {
      await post('/accounts/transfer', {
        requesting_user_id: customer.user_id,
        from_account_id: fromId,
        to_account_id: toId,
        amount: Number(amount),
      })
      setSubmitted(true)
      setAmount('')
      refetch()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Transfer failed.')
    }
  }

  return (
    <Layout>
      <PageWrapper>
        <PageTitle>Transfer Money</PageTitle>
        <PageSubtitle>Move money between your accounts in seconds.</PageSubtitle>

        {isLoading && <PageSubtitle>Loading your accounts…</PageSubtitle>}
        {loadError && <ErrorMessage role="alert">{loadError}</ErrorMessage>}

        {!isLoading && !loadError && (
          <TransferForm onSubmit={handleSubmit}>
            <FormGroup>
              <Label htmlFor="fromAccount">From account</Label>
              <Select id="fromAccount" name="fromAccount" value={fromId} onChange={(event) => setFromId(event.target.value)} required>
                {accounts.map((account) => (
                  <option key={account.account_id} value={account.account_id}>
                    {account.account_id} — {formatCurrency(account.balance)}
                  </option>
                ))}
              </Select>
            </FormGroup>

            <FormGroup>
              <Label htmlFor="toAccount">To account</Label>
              <Select id="toAccount" name="toAccount" value={toId} onChange={(event) => setToId(event.target.value)} required>
                {accounts.map((account) => (
                  <option key={account.account_id} value={account.account_id}>
                    {account.account_id} — {formatCurrency(account.balance)}
                  </option>
                ))}
              </Select>
            </FormGroup>

            <FormGroup>
              <Label htmlFor="amount">Amount</Label>
              <AmountField>
                <CurrencyPrefix aria-hidden="true">$</CurrencyPrefix>
                <AmountInput
                  id="amount"
                  name="amount"
                  type="number"
                  inputMode="decimal"
                  min="0.01"
                  step="0.01"
                  value={amount}
                  onChange={(event) => setAmount(event.target.value)}
                  required
                />
              </AmountField>
            </FormGroup>

            {error && (
              <ErrorMessage role="alert" id="transfer-error">
                {error}
              </ErrorMessage>
            )}

            <SubmitButton type="submit">Transfer Funds</SubmitButton>

            <StatusMessage role="status" aria-live="polite">
              {submitted ? 'Transfer completed successfully.' : ''}
            </StatusMessage>
          </TransferForm>
        )}
      </PageWrapper>
    </Layout>
  )
}

export default TransferPage
