/**
 * Stationsliste mit Führungslinie; Höhepunkte sitzen als größerer Punkt.
 * @startingPoint section="Daten" subtitle="Stationsliste der Route" viewport="700x360"
 */
export interface FactListProps {
  items: { name: string; note?: string; mark?: boolean }[];
  /** Zweispaltig ab 900 px — für lange Routenabschnitte */
  columns?: boolean;
}
export declare function FactList(props: FactListProps): JSX.Element;
