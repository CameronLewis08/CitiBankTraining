import { useAuth } from '../../Context/AuthContext'
import UserMenu from '../UserMenu/UserMenu'
import { HeaderWrapper, HeaderInner, Logo, Nav, NavLink, CtaButton } from './Header.styled'

function Header() {
  const { isLoggedIn, customer } = useAuth()
  const canViewDashboard = isLoggedIn && customer?.role !== 'Customer'

  return (
    <HeaderWrapper>
      <HeaderInner>
        <Logo to="/">Bank App</Logo>
        <Nav aria-label="Primary">
          <NavLink to="/" end>
            Home
          </NavLink>
          <NavLink to="/accounts">Accounts</NavLink>
          {canViewDashboard && <NavLink to="/admin">Dashboard</NavLink>}
          <NavLink to="/about">About</NavLink>
          <NavLink to="/contact">Contact</NavLink>
          {isLoggedIn ? <UserMenu /> : <CtaButton to="/login">Log In / Sign Up</CtaButton>}
        </Nav>
      </HeaderInner>
    </HeaderWrapper>
  )
}

export default Header
