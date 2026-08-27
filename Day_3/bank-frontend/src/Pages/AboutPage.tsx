import Layout from '../Components/Layout/Layout'
import { PageWrapper, PageTitle, PageSubtitle } from '../Components/PageHero/PageHero.styled'
import { CardGrid, Card, CardIcon, CardTitle, CardText } from '../Components/Card/Card.styled'

const values = [
  {
    icon: '🤝',
    title: 'Trust',
    text: 'We protect your money and your data with the same care we would want for our own.',
  },
  {
    icon: '💡',
    title: 'Simplicity',
    text: 'Banking should be easy to understand, not buried in fine print and jargon.',
  },
  {
    icon: '🌍',
    title: 'Access',
    text: 'Everyone deserves a bank account that works for them, wherever they are.',
  },
]

function AboutPage() {
  return (
    <Layout>
      <PageWrapper>
        <PageTitle>About Bank App</PageTitle>
        <PageSubtitle>
          Bank App was founded to make everyday banking simple, transparent, and accessible to everyone. We
          combine modern technology with the security and reliability you expect from a bank.
        </PageSubtitle>
        <CardGrid>
          {values.map((value) => (
            <Card key={value.title}>
              <CardIcon aria-hidden="true">{value.icon}</CardIcon>
              <CardTitle>{value.title}</CardTitle>
              <CardText>{value.text}</CardText>
            </Card>
          ))}
        </CardGrid>
      </PageWrapper>
    </Layout>
  )
}

export default AboutPage
