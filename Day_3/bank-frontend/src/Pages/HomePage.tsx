import Layout from '../Components/Layout/Layout'
import { useAuth } from '../Context/AuthContext'
import { useAccounts } from '../hooks/accounts/useAccounts'
import { formatCurrency } from '../data/accounts'
import { CardGrid, Card, CardLink, CardIcon, CardTitle, CardText, CardMeta, CardBalance } from '../Components/Card/Card.styled'
import { PrimaryButton, SecondaryButton } from '../Components/Button/Button.styled'
import { ErrorMessage } from '../Components/Form/Form.styled'
import { HomePageWrapper, Eyebrow, Title, Subtitle, ButtonRow } from './HomePage.styled'

const features = [
  {
    icon: '💳',
    title: 'Checking & Savings',
    text: 'Open an account in minutes and start earning interest right away.',
  },
  {
    icon: '📱',
    title: 'Mobile Banking',
    text: 'Check balances, transfer funds, and deposit checks from your phone.',
  },
  {
    icon: '🔒',
    title: 'Secure & Insured',
    text: 'Your deposits are protected with bank-level encryption and FDIC insurance.',
  },
]

function HomePage() {
  const { isLoggedIn, customer } = useAuth()
  // owner_id pinned to the logged-in user so the home page always shows
  // "your accounts," even for Admin/Manager, who'd otherwise see every
  // account or their whole branch's (AccountsService.get_all_accounts) -
  // that broader view belongs on the Admin Dashboard, not here.
  const { accounts, isLoading, error } = useAccounts(customer?.user_id, customer?.user_id)

  if (isLoggedIn) {
    return (
      <Layout>
        <HomePageWrapper>
          <Eyebrow>Welcome back, {customer?.name}</Eyebrow>
          <Title>Your accounts</Title>
          <Subtitle>Here's a snapshot of your balances. View details or send a transfer below.</Subtitle>
          <ButtonRow>
            <PrimaryButton to="/accounts">View Accounts</PrimaryButton>
            <SecondaryButton to="/transfer">Transfer Money</SecondaryButton>
          </ButtonRow>
          {isLoading && <Subtitle>Loading your accounts…</Subtitle>}
          {error && <ErrorMessage role="alert">{error}</ErrorMessage>}
          {!isLoading && !error && (
            <CardGrid>
              {accounts.map((account) => (
                <CardLink key={account.account_id} to={`/accounts/${account.account_id}`}>
                  <CardTitle>{account.account_id}</CardTitle>
                  <CardMeta>{account.account_type}</CardMeta>
                  <CardBalance>{formatCurrency(account.balance)}</CardBalance>
                </CardLink>
              ))}
            </CardGrid>
          )}
        </HomePageWrapper>
      </Layout>
    )
  }

  return (
    <Layout>
      <HomePageWrapper>
        <Eyebrow>Banking, simplified</Eyebrow>
        <Title>Welcome to Bank App</Title>
        <Subtitle>Manage your accounts, view balances, and track transactions all in one place.</Subtitle>
        <PrimaryButton to="/accounts">Open an Account</PrimaryButton>
        <CardGrid>
          {features.map((feature) => (
            <Card key={feature.title}>
              <CardIcon aria-hidden="true">{feature.icon}</CardIcon>
              <CardTitle>{feature.title}</CardTitle>
              <CardText>{feature.text}</CardText>
            </Card>
          ))}
        </CardGrid>
      </HomePageWrapper>
    </Layout>
  )
}

export default HomePage
