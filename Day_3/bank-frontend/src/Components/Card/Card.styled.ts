import { Link } from 'react-router-dom'
import styled from 'styled-components'

export const CardGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 1.5rem;
  width: 100%;
  max-width: 60rem;
  margin-top: 3rem;
`

export const Card = styled.div`
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.75rem;
  text-align: left;
  background: var(--code-bg);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow);
    border-color: var(--accent-border);
  }
`

export const CardLink = styled(Link)`
  display: block;
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.75rem;
  text-align: left;
  text-decoration: none;
  color: inherit;
  background: var(--code-bg);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow);
    border-color: var(--accent-border);
  }

  &:focus-visible {
    outline: 3px solid var(--accent-strong);
    outline-offset: 3px;
  }
`

export const CardIcon = styled.div`
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: var(--accent-bg);
  color: var(--accent);
  font-size: 1.5rem;
  margin-bottom: .5rem;
`

export const CardTitle = styled.h2`
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  color: var(--text-h);
`

export const CardText = styled.p`
  margin: 0;
  color: var(--text);
  font-size: 0.95rem;
  line-height: 1.5;
`

export const CardMeta = styled.p`
  margin: 0 0 0.75rem;
  color: var(--text);
  font-size: 0.85rem;
`

export const CardBalance = styled.p`
  margin: 0;
  color: var(--text-h);
  font-size: 1.6rem;
  font-weight: 700;
`

export const CardFooter = styled.div`
  margin-top: 1.25rem;
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
`
