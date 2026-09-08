import * as React from "react";

export interface FooterLink { href: string; label: string }

export interface SiteFooterProps {
  mark?: string;
  links?: FooterLink[];
  /** Fine print — sharing note, Impressum link. */
  children?: React.ReactNode;
}

export declare function SiteFooter(props: SiteFooterProps): JSX.Element;
