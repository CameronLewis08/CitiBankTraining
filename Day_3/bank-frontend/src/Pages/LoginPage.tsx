import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../Components/Layout/Layout'
import { useAuth } from '../Context/AuthContext'
import { post } from '../api/client'
import { PageWrapper, PageTitle, PageSubtitle } from '../Components/PageHero/PageHero.styled'
import { FormGroup, Label, Input, SubmitButton, ErrorMessage } from '../Components/Form/Form.styled'

import { SlideViewport, SlideTrack, SlidePanel, AuthForm, ToggleGroup, ToggleThumb, ToggleButton } from './LoginPage.styled'

type Mode = 'login' | 'signup'

function LoginPage() {
  const [mode, setMode] = useState<Mode>('login')
  const [error, setError] = useState('')
  const [signupError, setSignupError] = useState('')
  const { isLoggedIn, login } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (isLoggedIn) {
      navigate('/', { replace: true })
    }
  }, [isLoggedIn, navigate])

  function handleModeChange(nextMode: Mode) {
    setMode(nextMode)
  }

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
  event.preventDefault()
  setError('')

  const formData = new FormData(event.currentTarget)
  const email = formData.get('email') as string
  const password = formData.get('password') as string

  try 
  {
    await login(email, password)
    navigate('/')
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Something went wrong.')
  }
}

async function handleSignup(event: FormEvent<HTMLFormElement>) {
  event.preventDefault()
  setSignupError('')

  const formData = new FormData(event.currentTarget)
  const name = formData.get('fullName') as string
  const email = formData.get('email') as string
  const password = formData.get('password') as string
  const confirmPassword = formData.get('confirmPassword') as string

  if (password !== confirmPassword) {
    setSignupError('Passwords do not match.')
    return
  }

  try {
    // No role/requesting_user_id: this is the public self-signup path,
    // which the backend always creates as a Customer.
    await post('/users', { name, email, password })
    await login(email, password)
    navigate('/')
  } catch (err) {
    setSignupError(err instanceof Error ? err.message : 'Something went wrong.')
  }
}

  return (
    <Layout>
      <PageWrapper>
        <PageTitle>{mode === 'login' ? 'Welcome back' : 'Create your account'}</PageTitle>
        <PageSubtitle>
          {mode === 'login'
            ? 'Log in to check your balance, transfer funds, and manage your accounts.'
            : 'Sign up in minutes to open your first Bank App account.'}
        </PageSubtitle>

        <ToggleGroup role="group" aria-label="Choose log in or sign up">
          <ToggleThumb aria-hidden="true" $mode={mode} />
          <ToggleButton type="button" $active={mode === 'login'} aria-pressed={mode === 'login'} onClick={() => handleModeChange('login')}>
            Log In
          </ToggleButton>
          <ToggleButton type="button" $active={mode === 'signup'} aria-pressed={mode === 'signup'} onClick={() => handleModeChange('signup')}>
            Sign Up
          </ToggleButton>
        </ToggleGroup>

        <SlideViewport>
          <SlideTrack $mode={mode}>
            <SlidePanel>
              <AuthForm onSubmit={handleLogin} aria-hidden={mode !== 'login'} inert={mode !== 'login'}>
                <FormGroup>
                  <Label htmlFor="login-email">Email address</Label>
                  <Input id="login-email" name="email" type="email" autoComplete="email" required />
                </FormGroup>
                <FormGroup>
                  <Label htmlFor="login-password">Password</Label>
                  <Input id="login-password" name="password" type="password" autoComplete="current-password" required />
                </FormGroup>
                {error && <ErrorMessage role="alert">{error}</ErrorMessage>}
                <SubmitButton type="submit">Log In</SubmitButton>
              </AuthForm>
            </SlidePanel>
            <SlidePanel>
              <AuthForm onSubmit={handleSignup} aria-hidden={mode !== 'signup'} inert={mode !== 'signup'}>
                <FormGroup>
                  <Label htmlFor="signup-fullName">Full name</Label>
                  <Input id="signup-fullName" name="fullName" type="text" autoComplete="name" required />
                </FormGroup>
                <FormGroup>
                  <Label htmlFor="signup-email">Email address</Label>
                  <Input id="signup-email" name="email" type="email" autoComplete="email" required />
                </FormGroup>
                <FormGroup>
                  <Label htmlFor="signup-password">Password</Label>
                  <Input id="signup-password" name="password" type="password" autoComplete="new-password" required />
                </FormGroup>
                <FormGroup>
                  <Label htmlFor="signup-confirmPassword">Confirm password</Label>
                  <Input id="signup-confirmPassword" name="confirmPassword" type="password" autoComplete="new-password" required />
                </FormGroup>
                {signupError && <ErrorMessage role="alert">{signupError}</ErrorMessage>}
                <SubmitButton type="submit">Sign Up</SubmitButton>
              </AuthForm>
            </SlidePanel>
          </SlideTrack>
        </SlideViewport>
      </PageWrapper>
    </Layout>
  )
}

export default LoginPage
