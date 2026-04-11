import type { Metadata } from "next";
import "./globals.css";
import { ToastProvider } from "@/hooks/useToast";

export const metadata: Metadata = {
  title: "ContentForge AI - Content Repurposing Platform",
  description: "Transform your content into 20+ formats with AI-powered repurposing and distribution",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-gray-50">
        <ToastProvider>{children}</ToastProvider>
      </body>
    </html>
  );
}
