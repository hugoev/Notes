import { Inter } from 'next/font/google';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from 'next-themes';
import { useState } from 'react';
import { Toaster } from "@/components/ui/toaster";
import './globals.css';
import { ClientProviders } from '@/components/providers';

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Notes App',
  description: 'A modern note-taking application',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ClientProviders>
          {children}
          <Toaster />
        </ClientProviders>
      </body>
    </html>
  );
}