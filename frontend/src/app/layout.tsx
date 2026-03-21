import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'MedOrch',
  description: 'AI-driven bio-pharma intelligence platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} min-h-screen antialiased bg-[#0a0a0b] text-zinc-100 flex flex-col`}>
        <header className="border-b border-zinc-800/50 bg-[#0a0a0b]/80 backdrop-blur-xl sticky top-0 z-50">
          <div className="container mx-auto px-4 h-16 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
              </div>
              <span className="font-semibold tracking-tight text-xl bg-clip-text text-transparent bg-gradient-to-r from-zinc-100 to-zinc-400">
                Medic Orchestrator
              </span>
            </div>
            <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-zinc-400">
              <a href="/" className="hover:text-zinc-100 transition-colors">Platform</a>
              <a href="/agents" className="hover:text-zinc-100 transition-colors">Agents</a>
            </nav>
          </div>
        </header>
        <main className="flex-1 container mx-auto px-4 py-8">
          {children}
        </main>
        <footer className="border-t border-zinc-800/50 bg-[#0a0a0b]/80 backdrop-blur-xl print:hidden">
          <div className="container mx-auto px-4 py-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              <div className="col-span-1 md:col-span-2">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                    </svg>
                  </div>
                  <span className="font-semibold text-lg">Medic Orchestrator</span>
                </div>
                <p className="text-sm text-zinc-500 max-w-md">
                  AI-powered drug repurposing intelligence platform. Analyze molecules across clinical, patent, market, and regulatory domains in minutes.
                </p>
              </div>
              
              <div>
                <h3 className="font-semibold mb-3 text-sm uppercase tracking-wider text-zinc-400">Platform</h3>
                <ul className="space-y-2 text-sm text-zinc-500">
                  <li><a href="#" className="hover:text-zinc-300 transition">How it Works</a></li>
                  <li><a href="#" className="hover:text-zinc-300 transition">Data Sources</a></li>
                  <li><a href="#" className="hover:text-zinc-300 transition">API Access</a></li>
                </ul>
              </div>
              
              <div>
                <h3 className="font-semibold mb-3 text-sm uppercase tracking-wider text-zinc-400">Resources</h3>
                <ul className="space-y-2 text-sm text-zinc-500">
                  <li><a href="https://github.com/Surjithk73/medic-orchestrator" target="_blank" rel="noopener noreferrer" className="hover:text-zinc-300 transition">GitHub</a></li>
                  <li><a href="#" className="hover:text-zinc-300 transition">Documentation</a></li>
                  <li><a href="#" className="hover:text-zinc-300 transition">Support</a></li>
                </ul>
              </div>
            </div>
            
            <div className="mt-8 pt-8 border-t border-zinc-800/50 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-zinc-500">
              <p>© 2026 Medic Orchestrator. Built with LangGraph & Gemini AI.</p>
              <div className="flex items-center gap-4">
                <a href="#" className="hover:text-zinc-300 transition">Privacy</a>
                <a href="#" className="hover:text-zinc-300 transition">Terms</a>
                <a href="#" className="hover:text-zinc-300 transition">Contact</a>
              </div>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
