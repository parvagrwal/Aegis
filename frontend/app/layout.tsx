import "./globals.css"
import Header from "@/components/aegis/Header"
import VaultBackground from "@/components/aegis/VaultBackground"
import CommandDeck from "@/components/aegis/CommandDeck"

export default function RootLayout({children}:{children:React.ReactNode}){
  return (
    <html lang="en" data-theme="obsidian" suppressHydrationWarning>
      <head>
        <title>AEGIS Command Deck</title>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600;6..72,700&family=Inter:wght@400;500;700;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet" />
      </head>
      <body className="min-h-screen relative">
        <VaultBackground />
        <Header />
        <main className="mx-auto max-w-[1280px] px-4 md:px-6 py-6 grid grid-cols-1 lg:grid-cols-[320px_1fr_300px] gap-6">
          {children}
        </main>
        <footer className="py-8 text-center mono text-[11px] tracking-widest text-sage/60">Aegis Attestation · Sepolia · obsidian</footer>
        <div className="hidden lg:block fixed bottom-4 right-4 mono text-[11px] text-sage/70">⌘K · ⌘↵ SCAN</div>
        <CommandDeck />
      </body>
    </html>
  )
}
