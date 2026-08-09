/** Fußzeile mit Weitergabe-Bitte, Seitenliste und Impressum-Link. */
export interface SiteFooterProps {
  /** Text der Weitergabe-Bitte (ohne den fetten Vorspann) */
  note?: string;
  imprintHref?: string;
  baseline?: string;
}
export declare function SiteFooter(props: SiteFooterProps): JSX.Element;
