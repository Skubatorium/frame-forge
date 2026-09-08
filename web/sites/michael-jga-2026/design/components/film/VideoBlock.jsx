import React from "react";

/** 16:9 player plus info panels. Never autoplay, always poster + preload="metadata". */
export function VideoBlock({ src, poster, panels = [], children }) {
  return (
    <div className="video-block">
      <div className="video-block__player">
        <video controls preload="metadata" poster={poster} playsInline>
          <source src={src} type="video/mp4" />
          Dein Browser kann dieses Video nicht abspielen — lade die Datei stattdessen herunter.
        </video>
      </div>
      {panels.length > 0 && (
        <div className="video-block__info">
          {panels.map((p) => (
            <section className="video-block__panel" key={p.title}>
              <h3>{p.title}</h3>
              {p.rows ? (
                <dl className="video-block__dl">
                  {p.rows.map((r) => (
                    <React.Fragment key={r[0]}><dt>{r[0]}</dt><dd>{r[1]}</dd></React.Fragment>
                  ))}
                </dl>
              ) : <p>{p.text}</p>}
            </section>
          ))}
        </div>
      )}
      {children}
    </div>
  );
}
