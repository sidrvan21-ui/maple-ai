import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Maple AI",
  description: "Phase-gate product lifecycle workbench",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          fontFamily: "Georgia, 'Times New Roman', serif",
          background: "#f4efe6",
          color: "#1c1916",
        }}
      >
        {children}
      </body>
    </html>
  );
}
