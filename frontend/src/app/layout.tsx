import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL("https://scraper.pgdev.com.br"),
  title: "AI Web Scraper: a URL and a sentence become validated JSON",
  description:
    "Describe what you want in plain language and get back schema-validated JSON. Routes across GPT-5, Gemini 2.5 and Claude by cost, renders JavaScript pages, and refuses to invent a field it could not find.",
  authors: [{ name: "Pedro Gomes", url: "https://gomio.com.br" }],
  creator: "Pedro Gomes",
  // Sem openGraph/twitter o link vira URL crua no LinkedIn, no WhatsApp e no
  // Upwork — que e onde estas demos de facto circulam.
  openGraph: {
    type: "website",
    url: "https://scraper.pgdev.com.br",
    siteName: "Gomio",
    locale: "en_US",
    title: "AI Web Scraper: a URL and a sentence become validated JSON",
    description:
      "Describe what you want in plain language and get back schema-validated JSON. Routes across GPT-5, Gemini 2.5 and Claude by cost, renders JavaScript pages, and refuses to invent a field it could not find.",
    images: [{ url: "/og.png", width: 1200, height: 630, alt: "AI Web Scraper: natural language to structured JSON" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "AI Web Scraper: a URL and a sentence become validated JSON",
    description:
      "Describe what you want in plain language and get back schema-validated JSON. Routes across GPT-5, Gemini 2.5 and Claude by cost, renders JavaScript pages, and refuses to invent a field it could not find.",
    images: ["/og.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen bg-background`}
      >
        {children}
        <Toaster position="bottom-right" />
      </body>
    </html>
  );
}
