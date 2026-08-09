/**
 * Sticky Kopfzeile mit Flaggenmarke, Reisetitel und vier Seitenlinks.
 * @startingPoint section="Layout" subtitle="Sticky Kopfzeile über fünf Seiten" viewport="1280x120"
 */
export interface SiteNavProps {
  /** Dateiname der aktuellen Seite, setzt aria-current */
  current?: string;
  /** Reisetitel links */
  brand?: string;
  items?: { href: string; label: string }[];
}
export declare function SiteNav(props: SiteNavProps): JSX.Element;
