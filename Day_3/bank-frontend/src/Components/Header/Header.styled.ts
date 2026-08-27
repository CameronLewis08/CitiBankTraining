import { Link, NavLink as RouterNavLink } from 'react-router-dom'
import styled from 'styled-components'

export const HeaderWrapper = styled.header`
  position: sticky;
  top: 0;
  z-index: 10;
  border-bottom: 1px solid var(--border);
  background: color-mix(in srgb, var(--bg) 80%, transparent);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
`

export const HeaderInner = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  max-width: 1126px;
  margin: 0 auto;
  padding: 1.1rem 2rem;
  box-sizing: border-box;
`

export const Logo = styled(Link)`
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: -0.3px;
  color: var(--text-h);
  text-decoration: none;
`

export const Nav = styled.nav`
  display: flex;
  align-items: center;
  gap: 2rem;
`

export const NavLink = styled(RouterNavLink)`
  position: relative;
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  text-decoration: none;
  color: var(--text);
  font-size: 0.95rem;
  font-weight: 500;
  transition: color 0.15s ease;

  &::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: 10px;
    width: 0;
    height: 2px;
    background: var(--accent-strong);
    transition: width 0.2s ease;
  }

  &:hover {
    color: var(--text-h);
  }

  &:hover::after {
    width: 100%;
  }

  &.active {
    color: var(--text-h);
    font-weight: 700;
  }

  &.active::after {
    width: 100%;
  }
`

export const CtaButton = styled(Link)`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 700;
  color: #fff;
  background: var(--accent-strong);
  padding: 0.55rem 1.2rem;
  border-radius: 999px;
  transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;

  &:hover {
    background: var(--accent);
    transform: translateY(-1px);
    box-shadow: var(--shadow);
  }
`

export const LogoutButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  text-decoration: none;
  font: inherit;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--accent-strong);
  background: transparent;
  border: 2px solid var(--accent-strong);
  padding: calc(0.55rem - 2px) calc(1.2rem - 2px);
  border-radius: 999px;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease, color 0.15s ease;

  &:hover {
    background: var(--accent-strong);
    color: #fff;
    transform: translateY(-1px);
    box-shadow: var(--shadow);
  }
`
