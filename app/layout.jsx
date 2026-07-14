import "../styles.css";
import "./overrides.css";
import "./soft-theme.css";

export const metadata = {
  title: "Toneleaf — understand the feeling behind the words",
  description: "Private, in-browser sentiment and emotional distress signal analysis.",
  icons: { icon: "/icon.svg" },
  openGraph: {
    title: "Toneleaf",
    description: "Turn text into clearer emotional insight.",
    type: "website",
  },
};

export const viewport = { width: "device-width", initialScale: 1, themeColor: "#c4d4f2" };

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}
