import type { Metadata } from 'next';
import './globals.css';
import ReactQueryProvider from '@/components/ReactQueryProvider';
import { Sidebar } from '@/components/layout/Sidebar';
import { TopBar } from '@/components/layout/TopBar';
import { GlobalSpectraCopilot } from '@/components/copilot/GlobalSpectraCopilot';

export const metadata: Metadata = {
  title: 'Spectra-XDR // Enterprise Security Operations Console',
  description: 'AI-Powered Autonomous Multi-Agent XDR and Wazuh EDR Console',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="flex h-screen bg-[#fafafa] text-zinc-900 antialiased overflow-hidden font-sans selection:bg-zinc-900 selection:text-white">
        <ReactQueryProvider>
          <div className="flex w-full h-full">
            <Sidebar />
            <div className="flex-1 flex flex-col h-full overflow-hidden">
              <TopBar />
              <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-[#fafafa] swiss-grid-pattern">
                <div className="max-w-[1680px] mx-auto">
                  {children}
                </div>
              </main>
            </div>
          </div>
          <GlobalSpectraCopilot />
        </ReactQueryProvider>
      </body>
    </html>
  );
}
