import * as React from "react";

/**
 * Player 16:9 mit preload="metadata" und Poster. Nie Autoplay,
 * nie zwei Player auf derselben Seite.
 * @startingPoint section="Media" subtitle="Player 16:9 mit Bildunterzeile" viewport="1280x760"
 */
export interface VideoBlockProps {
  /** Absoluter Pfad, z. B. /videos/vlog-edit-1080p.mp4 */
  src: string;
  poster: string;
  /** Pfad zur .vtt-Datei; Platzhalter ist erlaubt */
  captionTrack?: string;
  /** Kurzangaben unter dem Player */
  meta?: React.ReactNode[];
  width?: number;
  height?: number;
}
export declare function VideoBlock(props: VideoBlockProps): JSX.Element;
