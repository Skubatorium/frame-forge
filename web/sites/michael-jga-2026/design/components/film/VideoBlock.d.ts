import * as React from "react";

export interface VideoPanel {
  title: string;
  /** Either free text… */
  text?: string;
  /** …or label/value rows (music credits, technical facts). */
  rows?: [string, string][];
}

export interface VideoBlockProps {
  /** Absolute server path, e.g. /videos/jga-2026-1080p.mp4 — the video is not part of the build. */
  src: string;
  poster: string;
  panels?: VideoPanel[];
  children?: React.ReactNode;
}

export declare function VideoBlock(props: VideoBlockProps): JSX.Element;
