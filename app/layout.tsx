"use client";

import "../styles/globals.css";
import { AuthProvider } from "../AuthProvider";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "DDQ Assistant",
  description: "AI-powered DDQ assistant",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
} 