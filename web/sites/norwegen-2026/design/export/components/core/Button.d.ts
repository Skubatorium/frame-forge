import * as React from "react";

/**
 * Aktionen: primär (eine je Seitenabschnitt), sekundär (Nebenweg),
 * download (Datei mit Größenangabe), ghost (Textlink-Charakter).
 * @startingPoint section="Core" subtitle="Primär, sekundär, Download, Ghost" viewport="700x140"
 */
export interface ButtonProps {
  /** Optische Variante */
  variant?: "primary" | "secondary" | "download" | "ghost";
  /** Wenn gesetzt, wird ein <a> gerendert */
  href?: string;
  /** Dateigröße rechts im Button, nur bei variant="download" */
  size?: string;
  /** Pfeil hinter dem Label (Weiterführung) */
  arrow?: boolean;
  disabled?: boolean;
  download?: boolean;
  onClick?: () => void;
  children?: React.ReactNode;
}
export declare function Button(props: ButtonProps): JSX.Element;
