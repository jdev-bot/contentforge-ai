import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ToastProvider } from "@/hooks/useToast";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { ThemeProvider } from "@/components/ThemeProvider";
import CookieConsent from "@/components/CookieConsent";
import { StagingBanner } from "@/components/StagingBanner";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

const APP_ENV = process.env.NEXT_PUBLIC_APP_ENV || 'production';
const isStaging = APP_ENV === 'staging';

export const metadata: Metadata = {
  title: "ContentForge AI - Content Repurposing Platform",
  description: "Transform your content into 20+ formats with AI-powered repurposing and distribution",
  keywords: ["AI", "content", "marketing", "social media", "repurposing"],
  authors: [{ name: "ContentForge" }],
  // Block indexing in staging
  ...(isStaging && {
    robots: {
      index: false,
      follow: false,
      nocache: true,
      googleBot: {
        index: false,
        follow: false,
        noimageindex: true,
      },
    },
  }),
  openGraph: {
    title: "ContentForge AI",
    description: "Transform your content with AI power",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning className={inter.variable}>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                // Check for saved theme preference or prefer-color-scheme
                const savedTheme = localStorage.getItem('theme');
                const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                
                if (savedTheme === 'dark' || (!savedTheme && systemDark)) {
                  document.documentElement.classList.add('dark');
                } else {
                  document.documentElement.classList.remove('dark');
                }
              })();
            `,
          }}
        />
      </head>
      <body className={`${inter.className} antialiased min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100`}>
        <ThemeProvider defaultTheme="system" storageKey="contentforge-theme">
          <ErrorBoundary>
            <ToastProvider>
              <StagingBanner />
              <div className={isStaging ? 'pt-8' : ''}>
                {children}
              </div>
              <CookieConsent />
            </ToastProvider>
          </ErrorBoundary>
        </ThemeProvider>
      </body>
    </html>
  );
}
