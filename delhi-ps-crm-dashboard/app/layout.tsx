import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/sidebar";

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
        <Sidebar />
        {/* mt-14 on mobile for top bar, md:ml-16 for tablet icon sidebar, lg:ml-64 for desktop full sidebar */}
        <main className="mt-14 flex-1 overflow-y-auto md:mt-0 md:ml-16 lg:ml-64">
          {children}
        </main>
      </body>
    </html>
  );
}
