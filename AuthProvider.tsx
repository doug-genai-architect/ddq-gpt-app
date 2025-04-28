// src/components/AuthProvider.tsx
"use client";

import React from "react";
import { MsalProvider } from "@azure/msal-react";
import { PublicClientApplication } from "@azure/msal-browser";
import { msalConfig } from "../lib/authConfig";

interface AuthProviderProps {
  children: React.ReactNode;
}

const msalInstance = new PublicClientApplication(msalConfig);

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  return (
    <MsalProvider instance={msalInstance}>
      {children}
    </MsalProvider>
  );
};

