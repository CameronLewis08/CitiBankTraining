import type { ReactNode } from 'react'
import Header from '../Header/Header'
import Footer from '../Footer/Footer'
import { MainContent } from './Layout.styled'

function Layout({ children }: { children: ReactNode }) {
  return (
    <>
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <Header />
      <MainContent id="main-content">{children}</MainContent>
      <Footer />
    </>
  )
}

export default Layout
