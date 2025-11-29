import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'DocuAI - Transform Unstructured Data into AI-Ready Insights',
  description: 'Convert PDFs, Word docs, and more into structured data for RAG, LLMs, and AI applications',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
