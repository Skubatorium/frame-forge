import * as React from "react";

export interface NavItem { href: string; label: string }

export interface NavProps {
  /** href of the page currently shown; gets aria-current. */
  current?: string;
  brand?: string;
  items?: NavItem[];
}

export declare function Nav(props: NavProps): JSX.Element;
