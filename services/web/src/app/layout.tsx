import { type Metadata } from "next";
import "@mantine/core/styles.css";
import { TRPCReactProvider } from "~/trpc/react";
import { MantineProvider } from "@mantine/core";
import { Navbar } from "./components/shared/Navbar";

export const metadata: Metadata = {
  title: "Screening Task",
  description: "",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <MantineProvider>
          <TRPCReactProvider>
            <Navbar />
            {children}
          </TRPCReactProvider>
        </MantineProvider>
      </body>
    </html>
  );
}
