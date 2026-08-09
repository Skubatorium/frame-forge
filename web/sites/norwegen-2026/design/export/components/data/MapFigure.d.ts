import * as React from "react";

/**
 * Kartenbild mit Bildunterschrift und externem Maps-Link.
 * Bewusst kein iframe — die Seite lädt nichts von fremden Servern.
 * @startingPoint section="Daten" subtitle="Kartenbild mit Maps-Link" viewport="1280x600"
 */
export interface MapFigureProps {
  src: string;
  alt: string;
  /** Erklärt, welcher Teil der Reise zu sehen ist */
  caption: React.ReactNode;
  href?: string;
  linkLabel?: string;
  width?: number;
  height?: number;
}
export declare function MapFigure(props: MapFigureProps): JSX.Element;
