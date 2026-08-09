import React from "react";

export function HeroRotator({ scenes = [], eyebrow, title, meta, children }) {
  return (
    <section className="hero" aria-label={title}>
      <div className="hero__scenes" aria-hidden="true" style={scenes[0] ? { backgroundImage: "url(" + scenes[0] + ")" } : undefined}>
        {scenes.map((src, i) => (
          <img key={src} className="hero__scene" style={{ "--i": i, "--n": scenes.length }} src={src} alt="" />
        ))}
      </div>
      <div className="hero__scrim" aria-hidden="true"></div>
      <div className="wrap hero__inner">
        {eyebrow ? <p className="eyebrow hero__eyebrow">{eyebrow}</p> : null}
        <h1 className="hero__title">{title}</h1>
        {meta ? <p className="hero__meta">{meta}</p> : null}
        {children ? <div className="hero__actions">{children}</div> : null}
      </div>
    </section>
  );
}
