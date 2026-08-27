import { FooterWrapper } from './Footer.styled'

function Footer() {
  return (
    <FooterWrapper>
      <p>&copy; {new Date().getFullYear()} Bank App. All rights reserved.</p>
    </FooterWrapper>
  )
}

export default Footer
