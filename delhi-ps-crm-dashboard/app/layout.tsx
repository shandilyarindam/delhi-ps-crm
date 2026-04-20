import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/sidebar";
import ErrorBoundary from "@/components/error-boundary";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "Delhi PS-CRM | Civic Grievance Portal",
  description:
    "AI-Powered WhatsApp Civic Complaint Management System for Delhi",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} h-full antialiased`}
    >
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="flex h-full min-h-screen bg-[#F0F2F5] font-[family-name:var(--font-inter)]">
        <ErrorBoundary
          fallback={
            <div className="flex h-full items-center justify-center bg-[#F0F2F5]">
              <div className="text-center">
                <h1 className="text-2xl font-bold text-red-600 mb-4">Something went wrong</h1>
                <p className="text-gray-600 mb-6">We're sorry, but something unexpected happened.</p>
                <button
                  onClick={() => window.location.reload()}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Reload Page
                </button>
              </div>
            </div>
          }
        >
          <Sidebar />
          {/* mt-14 on mobile for top bar, md:ml-16 for tablet icon sidebar, lg:ml-64 for desktop full sidebar */}
          <main className="mt-14 flex-1 overflow-y-auto md:mt-0 md:ml-16 lg:ml-64">
            <ErrorBoundary
              fallback={
                <div className="flex h-full items-center justify-center">
                  <div className="text-center">
                    <h2 className="text-xl font-semibold text-red-600 mb-2">Content Error</h2>
                    <p className="text-gray-600 mb-4">This section failed to load.</p>
                    <button
                      onClick={() => window.location.reload()}
                      className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                    >
                      Reload
                    </button>
                  </div>
                </div>
              }
            >
              {children}
            </ErrorBoundary>
          </main>
        </ErrorBoundary>
      </body>
    </html>
  );
}
