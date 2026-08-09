import * as React from "react";

/**
 * Schmaler Seitenkopf der Unterseiten — kein Bild, kein Vollbild.
 * @startingPoint section="Layout" subtitle="Kopf einer Unterseite" viewport="1280x340"
 */
export interface PageHeaderProps {
  /** Kleinversalien-Zeile über dem Titel, z. B. "Film 1" */
  eyebrow?: string;
  title: string;
  /** Ein Satz Einordnung */
  sub?: React.ReactNode;
  /** Kerndaten als Liste, z. B. ["18:00 min", "3840 × 2160"] */
  meta?: React.ReactNode[];
  /** Ohne Verlaufshintergrund */
  quiet?: boolean;
}
export declare function PageHeader(props: PageHeaderProps): JSX.Element;
