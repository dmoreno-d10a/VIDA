import type { Metadata, Viewport } from "next";

import "./global.css";

export const metadata: Metadata = {
  title: "V.I.D.A.",
  description:
    "Vortexbird Intelligent Documentation Assistant — plataforma de los Requirements Owners de VortexBird.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

/** Estructura común de todas las pantallas. La plataforma está en español (Art. XII). */
export default function EstructuraRaiz({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
