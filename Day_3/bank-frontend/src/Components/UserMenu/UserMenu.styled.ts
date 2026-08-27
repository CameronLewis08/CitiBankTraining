import { Link } from 'react-router-dom'
import styled from 'styled-components'

export const MenuWrapper = styled.div`
  position: relative;
`

export const TriggerButton = styled.button`
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  min-height: 44px;
  font: inherit;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--accent-strong);
  background: transparent;
  border: 2px solid var(--accent-strong);
  padding: calc(0.55rem - 2px) calc(1rem - 2px);
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

export const Caret = styled.span<{ $open: boolean }>`
  display: inline-block;
  font-size: 0.7rem;
  transition: transform 0.15s ease;
  transform: rotate(${({ $open }) => ($open ? '180deg' : '0deg')});
`

export const MenuPanel = styled.div`
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  min-width: 12rem;
  display: flex;
  flex-direction: column;
  padding: 0.4rem;
  gap: 0.15rem;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: var(--shadow);
  z-index: 20;
`

const menuItemStyles = `
  display: block;
  width: 100%;
  text-align: left;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  font: inherit;
  font-size: 0.9rem;
  color: var(--text-h);
  background: transparent;
  border: none;
  text-decoration: none;
  cursor: pointer;
`

export const MenuLink = styled(Link)`
  ${menuItemStyles}

  &:hover {
    background: var(--accent-bg);
  }
`

export const MenuButton = styled.button`
  ${menuItemStyles}

  &:hover {
    background: var(--accent-bg);
  }
`
