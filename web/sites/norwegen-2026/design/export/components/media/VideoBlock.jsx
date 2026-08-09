import React from "react";

export function VideoBlock({ src, poster, captionTrack, meta = [], width = 1920, height = 1080 }) {
  return (
    <div className="video-block">
      <div className="video-block__frame">
        <video controls preload="metadata" playsInline poster={poster} width={width} height={height}>
          <source src={src} type="video/mp4" />
          {captionTrack ? <track kind="captions" srcLang="de" label="Deutsch" src={captionTrack} /> : null}
          <p>Dein Browser kann dieses Video nicht abspielen. <a href={src}>Direkt herunterladen</a>.</p>
        </video>
      </div>
      {meta.length ? <p className="video-block__caption">{meta.map((m, i) => <span key={i}>{m}</span>)}</p> : null}
    </div>
  );
}
