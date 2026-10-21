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

// The previous copy promised "schema-validated JSON" and a scraper that
// "refuses to invent a field". Without a schema nothing is validated
// (validation_passed is null), and a model can still guess. The text below
// says only what the code does: validation runs when a schema is defined, and
// the prompt tells the model to return null instead of inferring.
const TITLE = "AI Web Scraper: a URL and a sentence become structured JSON";
const DESCRIPTION =
  "Describe what you want in plain language and get structured JSON back from a public web page. Renders JavaScript pages, routes across GPT-5, Gemini 2.5 and Claude by cost, checks the output against your schema when you define one, and tells the model to return null instead of guessing.";

// No `title` here on purpose: the page renders a React <title> in the visitor's
// language (see I18nProvider). A metadata title is re-applied by Next after
// hydration and would pin the tab to English with PT selected. The prerendered
// HTML still carries the English title, so crawlers see the same text.
export const metadata: Metadata = {
  metadataBase: new URL("https://scraper.pgdev.com.br"),
  description: DESCRIPTION,
  authors: [{ name: "Pedro Gomes", url: "https://gomio.com.br" }],
  creator: "Pedro Gomes",
  // Sem openGraph/twitter o link vira URL crua no LinkedIn, no WhatsApp e no
  // Upwork — que e onde estas demos de facto circulam.
  openGraph: {
    type: "website",
    url: "https://scraper.pgdev.com.br",
    siteName: "Gomio",
    locale: "en_US",
    title: TITLE,
    description: DESCRIPTION,
    images: [{ url: "/og.png", width: 1200, height: 630, alt: "AI Web Scraper: natural language to structured JSON" }],
  },
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESCRIPTION,
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
