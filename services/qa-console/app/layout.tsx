import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "Lead Intelligence — QA Console",
  description: "Internal reviewer gate for delivered accounts",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav>
          <strong>Lead Intelligence</strong>
          <a href="/">Review queue</a>
          <a href="/merge">Merge queue</a>
          <a href="/costs">Cost board</a>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}
