/**
 * Teaser-Karte für einen Film: Standbild, Verlauf, Titel, ein Satz, Button.
 * @startingPoint section="Media" subtitle="Teaser-Karte für einen Film" viewport="700x440"
 */
export interface FilmCardProps {
  image: string;
  /** Alt-Text des Standbilds — beschreibt das Motiv, nicht den Film */
  alt?: string;
  /** Zeile über dem Titel, z. B. "Film 1 · 18:00 min" */
  kicker?: string;
  title: string;
  text?: string;
  href: string;
  cta?: string;
}
export declare function FilmCard(props: FilmCardProps): JSX.Element;
