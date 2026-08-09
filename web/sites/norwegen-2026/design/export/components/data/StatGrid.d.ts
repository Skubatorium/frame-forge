/**
 * Kennzahlen-Raster: Zahl groß, Einheit klein, Label in Kleinversalien.
 * @startingPoint section="Daten" subtitle="Kennzahlen-Raster" viewport="1280x180"
 */
export interface StatGridProps {
  items: { value: string; unit?: string; label: string }[];
  /** 4 (Standard) oder 3 Spalten ab 720 px */
  columns?: 3 | 4;
  /** Dunklere Kacheln, für Zonen auf --bg-page */
  sunken?: boolean;
}
export declare function StatGrid(props: StatGridProps): JSX.Element;
