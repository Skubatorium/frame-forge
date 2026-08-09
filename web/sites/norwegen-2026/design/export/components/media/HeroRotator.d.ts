import * as React from "react";

/**
 * Vollbild-Hero mit langsam überblendenden Standbildern (reines CSS).
 * Respektiert prefers-reduced-motion: dann Standbild statt Rotation.
 * @startingPoint section="Media" subtitle="Vollbild-Hero mit Bildrotation" viewport="1280x720"
 */
export interface HeroRotatorProps {
  /** 4–6 Bildpfade; die Keyframes sind auf sechs Szenen abgestimmt */
  scenes: string[];
  eyebrow?: string;
  title: string;
  /** Zeile unter dem Titel, z. B. "18 Tage · 3.829 km" */
  meta?: React.ReactNode;
  /** Buttons */
  children?: React.ReactNode;
}
export declare function HeroRotator(props: HeroRotatorProps): JSX.Element;
