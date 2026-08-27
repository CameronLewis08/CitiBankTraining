import styled from 'styled-components'

export const HomePageWrapper = styled.section`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1.25rem;
  padding: 5.5rem 2rem 4rem;
  text-align: center;
`

export const Eyebrow = styled.span`
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent-text);
  background: var(--accent-bg);
  border: 1px solid var(--accent-border);
  padding: 0.35rem 0.9rem;
  border-radius: 999px;
`

export const Title = styled.h1`
  font-size: 3.2rem;
  line-height: 1.1;
  margin: 0.5rem 0 0;
  background: linear-gradient(135deg, var(--text-h), var(--accent));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;

  @media (max-width: 1024px) {
    font-size: 2.2rem;
  }
`

export const Subtitle = styled.p`
  font-size: 1.1rem;
  line-height: 1.6;
  color: var(--text);
  max-width: 34rem;
`

export const ButtonRow = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
`

