import styled from 'styled-components'

export const PageWrapper = styled.section`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 4rem 2rem 3rem;
  text-align: center;
`

export const PageTitle = styled.h1`
  font-size: 2.6rem;
  margin: 0;
  color: var(--text-h);

  @media (max-width: 1024px) {
    font-size: 2rem;
  }
`

export const PageSubtitle = styled.p`
  font-size: 1.05rem;
  line-height: 1.6;
  color: var(--text);
  max-width: 36rem;
`
