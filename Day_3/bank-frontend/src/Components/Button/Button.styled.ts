import { Link } from 'react-router-dom'
import styled from 'styled-components'

export const PrimaryButton = styled(Link)`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  text-decoration: none;
  font-size: 1rem;
  font-weight: 700;
  color: #fff;
  background: var(--accent-strong);
  padding: 0.85rem 1.8rem;
  border-radius: 999px;
  transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;

  &:hover {
    background: var(--accent);
    transform: translateY(-2px);
    box-shadow: var(--shadow);
  }

  &:focus-visible {
    outline: 3px solid var(--accent-strong);
    outline-offset: 3px;
  }
`

export const SecondaryButton = styled(Link)`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  text-decoration: none;
  font-size: 1rem;
  font-weight: 700;
  color: var(--accent-strong);
  background: transparent;
  border: 2px solid var(--accent-strong);
  padding: calc(0.85rem - 2px) calc(1.8rem - 2px);
  border-radius: 999px;
  transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease, color 0.15s ease;

  &:hover {
    background: var(--accent-strong);
    color: #fff;
    transform: translateY(-2px);
    box-shadow: var(--shadow);
  }

  &:focus-visible {
    outline: 3px solid var(--accent-strong);
    outline-offset: 3px;
  }
`
