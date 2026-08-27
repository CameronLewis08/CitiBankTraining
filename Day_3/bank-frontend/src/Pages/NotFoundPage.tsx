import Layout from '../Components/Layout/Layout'
import { PageWrapper, PageTitle, PageSubtitle } from '../Components/PageHero/PageHero.styled'
import { PrimaryButton } from '../Components/Button/Button.styled'

function NotFoundPage() {
  return (
    <Layout>
      <PageWrapper>
        <PageTitle>Page not found</PageTitle>
        <PageSubtitle>The page you're looking for doesn't exist or may have moved.</PageSubtitle>
        <PrimaryButton to="/">Back to Home</PrimaryButton>
      </PageWrapper>
    </Layout>
  )
}

export default NotFoundPage
