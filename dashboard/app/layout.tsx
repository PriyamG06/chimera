import type { Metadata } from "next";
import { Instrument_Serif, Hanken_Grotesk, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

const serif = Instrument_Serif({
  weight: "400",
  subsets: ["latin"],
  display: "swap",
  variable: "--font-serif",
});

const sans = Hanken_Grotesk({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-sans",
});

const mono = IBM_Plex_Mono({
  weight: ["400", "500", "600"],
  subsets: ["latin"],
  display: "swap",
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "Project Chimera · Eval & Error",
  description:
    "Capability is easy. Consistency is the story. Six frontier models dropped into a failing marketplace, scored on product judgment over 60 simulated days.",
  openGraph: {
    title: "Project Chimera · Eval & Error",
    description:
      "Six frontier models, one autonomous product-judgment gauntlet. Capability is easy; consistency is the story.",
    type: "article",
  },
};

const FOUC_SCRIPT = `
(function() {
  try {
    var stored = localStorage.getItem('theme');
    if (stored === 'dark' || stored === 'light') {
      document.documentElement.setAttribute('data-theme', stored);
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      document.documentElement.setAttribute('data-theme', 'dark');
    }
  } catch (e) {}
})();
`.trim();

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${serif.variable} ${sans.variable} ${mono.variable}`}
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: FOUC_SCRIPT }} />
        <noscript>
          <style>{`.reveal{opacity:1 !important}`}</style>
        </noscript>
      </head>
      <body>{children}</body>
    </html>
  );
}
