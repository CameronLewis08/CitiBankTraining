import { useAuth } from '../../Context/AuthContext'
import { HeaderWrapper, HeaderInner, Logo, Nav, NavLink, CtaButton, LogoutButton } from './Header.styled'

function Header() {
  const { isLoggedIn, logout } = useAuth()

  return (
    <HeaderWrapper>
      <HeaderInner>
        <Logo to="/">Bank App</Logo>
        <Nav aria-label="Primary">
          <NavLink to="/" end>
            Home
          </NavLink>
          <NavLink to="/accounts">Accounts</NavLink>
          <NavLink to="/about">About</NavLink>
          <NavLink to="/contact">Contact</NavLink>
          {isLoggedIn ? (
            <LogoutButton type="button" onClick={logout}>
              Log Out
            </LogoutButton>
          ) : (
            <CtaButton to="/login">Log In / Sign Up</CtaButton>
          )}
        </Nav>
      </HeaderInner>
    </HeaderWrapper>
  )
}

export default Header
