import { useState } from 'react'
import type { FormEvent } from 'react'
import Layout from '../Components/Layout/Layout'
import { PageWrapper, PageTitle, PageSubtitle } from '../Components/PageHero/PageHero.styled'
import { FormGroup, Label, Input, TextArea, SubmitButton, StatusMessage } from '../Components/Form/Form.styled'
import { ContactForm } from './ContactPage.styled'

function ContactPage() {
  const [submitted, setSubmitted] = useState(false)

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitted(true)
  }

  return (
    <Layout>
      <PageWrapper>
        <PageTitle>Contact Us</PageTitle>
        <PageSubtitle>Have a question about your account or our services? Send us a message and we'll get back to you.</PageSubtitle>
        <ContactForm onSubmit={handleSubmit}>
          <FormGroup>
            <Label htmlFor="name">Full name</Label>
            <Input id="name" name="name" type="text" autoComplete="name" required />
          </FormGroup>
          <FormGroup>
            <Label htmlFor="email">Email address</Label>
            <Input id="email" name="email" type="email" autoComplete="email" required />
          </FormGroup>
          <FormGroup>
            <Label htmlFor="message">Message</Label>
            <TextArea id="message" name="message" required />
          </FormGroup>
          <SubmitButton type="submit">Send Message</SubmitButton>
          <StatusMessage role="status" aria-live="polite">
            {submitted ? 'Thanks! Your message has been sent.' : ''}
          </StatusMessage>
        </ContactForm>
      </PageWrapper>
    </Layout>
  )
}

export default ContactPage
