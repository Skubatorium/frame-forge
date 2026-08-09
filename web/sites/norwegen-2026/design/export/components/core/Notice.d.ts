import * as React from "react";

/** Dezenter Hinweiskasten — nie rot, nie alarmierend. */
export interface NoticeProps {
  /** Kleinversalien-Überschrift, z. B. "Zur Genauigkeit" */
  title?: string;
  /** Ohne Flächenfüllung, nur Linie */
  quiet?: boolean;
  children?: React.ReactNode;
}
export declare function Notice(props: NoticeProps): JSX.Element;
