import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TalentMatch — Work that fits",
  description: "Thoughtful job matches for the work you want to do next.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
