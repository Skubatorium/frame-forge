/* @ds-bundle: {"format":4,"namespace":"MichaImDeliriumJGADesignSystem_c29a45","components":[{"name":"Button","sourcePath":"components/core/Button.jsx"},{"name":"MarkerCaption","sourcePath":"components/core/MarkerCaption.jsx"},{"name":"Notice","sourcePath":"components/core/Notice.jsx"},{"name":"Prose","sourcePath":"components/core/Prose.jsx"},{"name":"Sticker","sourcePath":"components/core/Sticker.jsx"},{"name":"CastGrid","sourcePath":"components/film/CastGrid.jsx"},{"name":"PlayTeaser","sourcePath":"components/film/PlayTeaser.jsx"},{"name":"QualityBox","sourcePath":"components/film/QualityBox.jsx"},{"name":"VideoBlock","sourcePath":"components/film/VideoBlock.jsx"},{"name":"Nav","sourcePath":"components/site/Nav.jsx"},{"name":"PageHeader","sourcePath":"components/site/PageHeader.jsx"},{"name":"SiteFooter","sourcePath":"components/site/SiteFooter.jsx"}],"sourceHashes":{"components/core/Button.jsx":"71933332c70e","components/core/MarkerCaption.jsx":"61c7c7fb0591","components/core/Notice.jsx":"3c9ef2273151","components/core/Prose.jsx":"d243032c8777","components/core/Sticker.jsx":"a1ce449320c1","components/film/CastGrid.jsx":"020ab4c38e5e","components/film/PlayTeaser.jsx":"cacef0f03149","components/film/QualityBox.jsx":"ac5a0a6200d8","components/film/VideoBlock.jsx":"6e2e4603a2eb","components/site/Nav.jsx":"18e45af1fffa","components/site/PageHeader.jsx":"a154b7e219d4","components/site/SiteFooter.jsx":"e3ca31466669"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.MichaImDeliriumJGADesignSystem_c29a45 = window.MichaImDeliriumJGADesignSystem_c29a45 || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/core/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function Button({
  as,
  variant = "primary",
  children,
  className = "",
  ...rest
}) {
  const Tag = as || (rest.href ? "a" : "button");
  return /*#__PURE__*/React.createElement(Tag, _extends({
    className: `btn btn--${variant} ${className}`.trim()
  }, rest), children);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Button.jsx", error: String((e && e.message) || e) }); }

// components/core/MarkerCaption.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/** Hand-marker caption with a rough underline stroke, as on the poster edges. */
function MarkerCaption({
  children,
  rotate = -4,
  className = "",
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("span", _extends({
    className: `marker-caption ${className}`.trim(),
    style: {
      transform: `rotate(${rotate}deg)`,
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { MarkerCaption });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/MarkerCaption.jsx", error: String((e && e.message) || e) }); }

// components/core/Notice.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function Notice({
  mark = "!",
  tone = "quiet",
  children,
  className = "",
  ...rest
}) {
  return /*#__PURE__*/React.createElement("aside", _extends({
    className: `notice${tone === "loud" ? " notice--loud" : ""} ${className}`.trim()
  }, rest), /*#__PURE__*/React.createElement("span", {
    className: "notice__mark",
    "aria-hidden": "true"
  }, mark), /*#__PURE__*/React.createElement("div", {
    className: "notice__body"
  }, children));
}
Object.assign(__ds_scope, { Notice });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Notice.jsx", error: String((e && e.message) || e) }); }

// components/core/Prose.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/** Readable text column inside the loud surroundings. */
function Prose({
  wide = false,
  children,
  className = "",
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    className: `prose${wide ? " prose--wide" : ""} ${className}`.trim()
  }, rest), children);
}
Object.assign(__ds_scope, { Prose });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Prose.jsx", error: String((e && e.message) || e) }); }

// components/core/Sticker.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/** Neon doodle accent — a crown, star or heart glyph, glowing, CSS-only. */
function Sticker({
  glyph = "★",
  tone = "pink",
  size = "md",
  still = false,
  style,
  className = "",
  ...rest
}) {
  const tones = {
    pink: "",
    gold: " sticker--gold",
    cyan: " sticker--cyan"
  };
  const sizes = {
    sm: " sticker--sm",
    md: "",
    lg: " sticker--lg"
  };
  return /*#__PURE__*/React.createElement("span", _extends({
    "aria-hidden": "true",
    style: style,
    className: `sticker${tones[tone] || ""}${sizes[size] || ""}${still ? " sticker--still" : ""} ${className}`.trim()
  }, rest), glyph);
}
Object.assign(__ds_scope, { Sticker });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Sticker.jsx", error: String((e && e.message) || e) }); }

// components/film/CastGrid.jsx
try { (() => {
/** The ten sunglasses portraits as comic stamps. `groom` gets the cyan special accent. */
function CastGrid({
  members = []
}) {
  return /*#__PURE__*/React.createElement("ul", {
    className: "cast-grid"
  }, members.map((m, i) => /*#__PURE__*/React.createElement("li", {
    key: m.name || i,
    className: `cast-card${m.groom ? " cast-card--groom" : ""}`
  }, /*#__PURE__*/React.createElement("span", {
    className: "cast-card__frame"
  }, /*#__PURE__*/React.createElement("img", {
    src: m.photo,
    alt: m.alt || `${m.name} mit Sonnenbrille`,
    loading: "lazy"
  })), /*#__PURE__*/React.createElement("p", {
    className: "cast-card__name"
  }, m.name), m.role && /*#__PURE__*/React.createElement("p", {
    className: "cast-card__role"
  }, m.role))));
}
Object.assign(__ds_scope, { CastGrid });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/film/CastGrid.jsx", error: String((e && e.message) || e) }); }

// components/film/PlayTeaser.jsx
try { (() => {
function PlayTeaser({
  href = "film.html",
  poster,
  title,
  meta,
  alt = ""
}) {
  return /*#__PURE__*/React.createElement("a", {
    className: "play-teaser",
    href: href
  }, /*#__PURE__*/React.createElement("img", {
    src: poster,
    alt: alt
  }), /*#__PURE__*/React.createElement("span", {
    className: "play-teaser__veil"
  }, /*#__PURE__*/React.createElement("span", {
    className: "play-teaser__badge",
    "aria-hidden": "true"
  }, /*#__PURE__*/React.createElement("svg", {
    viewBox: "0 0 24 24",
    role: "presentation"
  }, /*#__PURE__*/React.createElement("path", {
    d: "M8 5.5v13l11-6.5z"
  }))), /*#__PURE__*/React.createElement("span", {
    className: "play-teaser__title"
  }, title), meta && /*#__PURE__*/React.createElement("span", {
    className: "play-teaser__meta"
  }, meta)));
}
Object.assign(__ds_scope, { PlayTeaser });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/film/PlayTeaser.jsx", error: String((e && e.message) || e) }); }

// components/film/QualityBox.jsx
try { (() => {
/** Streaming vs. Download side by side. */
function QualityBox({
  options = []
}) {
  return /*#__PURE__*/React.createElement("div", {
    className: "quality-box"
  }, options.map(o => /*#__PURE__*/React.createElement("article", {
    className: `quality-option${o.recommended ? " quality-option--recommended" : ""}`,
    key: o.title
  }, o.tag && /*#__PURE__*/React.createElement("span", {
    className: "quality-option__tag"
  }, o.tag), /*#__PURE__*/React.createElement("h3", {
    className: "quality-option__title"
  }, o.title), /*#__PURE__*/React.createElement("p", {
    className: "quality-option__spec"
  }, o.spec), /*#__PURE__*/React.createElement("p", {
    className: "quality-option__text"
  }, o.text), o.hint && /*#__PURE__*/React.createElement("p", {
    className: "quality-option__hint"
  }, o.hint), o.action && /*#__PURE__*/React.createElement(__ds_scope.Button, {
    href: o.action.href,
    download: o.action.download || undefined,
    variant: o.recommended ? "primary" : "secondary"
  }, o.action.label))));
}
Object.assign(__ds_scope, { QualityBox });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/film/QualityBox.jsx", error: String((e && e.message) || e) }); }

// components/film/VideoBlock.jsx
try { (() => {
/** 16:9 player plus info panels. Never autoplay, always poster + preload="metadata". */
function VideoBlock({
  src,
  poster,
  panels = [],
  children
}) {
  return /*#__PURE__*/React.createElement("div", {
    className: "video-block"
  }, /*#__PURE__*/React.createElement("div", {
    className: "video-block__player"
  }, /*#__PURE__*/React.createElement("video", {
    controls: true,
    preload: "metadata",
    poster: poster,
    playsInline: true
  }, /*#__PURE__*/React.createElement("source", {
    src: src,
    type: "video/mp4"
  }), "Dein Browser kann dieses Video nicht abspielen \u2014 lade die Datei stattdessen herunter.")), panels.length > 0 && /*#__PURE__*/React.createElement("div", {
    className: "video-block__info"
  }, panels.map(p => /*#__PURE__*/React.createElement("section", {
    className: "video-block__panel",
    key: p.title
  }, /*#__PURE__*/React.createElement("h3", null, p.title), p.rows ? /*#__PURE__*/React.createElement("dl", {
    className: "video-block__dl"
  }, p.rows.map(r => /*#__PURE__*/React.createElement(React.Fragment, {
    key: r[0]
  }, /*#__PURE__*/React.createElement("dt", null, r[0]), /*#__PURE__*/React.createElement("dd", null, r[1])))) : /*#__PURE__*/React.createElement("p", null, p.text)))), children);
}
Object.assign(__ds_scope, { VideoBlock });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/film/VideoBlock.jsx", error: String((e && e.message) || e) }); }

// components/site/Nav.jsx
try { (() => {
const links = [{
  href: "index.html",
  label: "Start"
}, {
  href: "film.html",
  label: "Der Film"
}, {
  href: "impressum.html",
  label: "Impressum"
}];
function Nav({
  current = "index.html",
  brand = "Micha im Delirium",
  items = links
}) {
  return /*#__PURE__*/React.createElement("nav", {
    className: "nav",
    "aria-label": "Hauptnavigation"
  }, /*#__PURE__*/React.createElement("div", {
    className: "nav__inner"
  }, /*#__PURE__*/React.createElement("a", {
    className: "nav__brand",
    href: "index.html"
  }, brand), /*#__PURE__*/React.createElement("ul", {
    className: "nav__list"
  }, items.map(l => /*#__PURE__*/React.createElement("li", {
    key: l.href
  }, /*#__PURE__*/React.createElement("a", {
    className: "nav__link",
    href: l.href,
    "aria-current": l.href === current ? "page" : undefined
  }, l.label))))));
}
Object.assign(__ds_scope, { Nav });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/site/Nav.jsx", error: String((e && e.message) || e) }); }

// components/site/PageHeader.jsx
try { (() => {
/** Cinema-poster masthead. `variant="quiet"` is the plain-caps voice for subpages. */
function PageHeader({
  kicker,
  title,
  sub,
  image,
  imageAlt = "",
  variant = "loud",
  children
}) {
  const quiet = variant === "quiet";
  return /*#__PURE__*/React.createElement("header", {
    className: `page-header${quiet ? " page-header--quiet" : ""}`
  }, !quiet && image && /*#__PURE__*/React.createElement("div", {
    className: "page-header__media"
  }, /*#__PURE__*/React.createElement("img", {
    src: image,
    alt: imageAlt
  })), /*#__PURE__*/React.createElement("div", {
    className: "page-header__body"
  }, kicker && (quiet ? /*#__PURE__*/React.createElement("p", {
    className: "ruled-caps"
  }, kicker) : /*#__PURE__*/React.createElement("p", {
    className: "page-header__kicker"
  }, kicker)), /*#__PURE__*/React.createElement("h1", {
    className: "page-header__title"
  }, title), sub && /*#__PURE__*/React.createElement("p", {
    className: "page-header__sub"
  }, sub), children));
}
Object.assign(__ds_scope, { PageHeader });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/site/PageHeader.jsx", error: String((e && e.message) || e) }); }

// components/site/SiteFooter.jsx
try { (() => {
function SiteFooter({
  mark = "Micha im Delirium 2026",
  links = [],
  children
}) {
  return /*#__PURE__*/React.createElement("footer", {
    className: "footer"
  }, /*#__PURE__*/React.createElement("div", {
    className: "footer__inner"
  }, /*#__PURE__*/React.createElement("p", {
    className: "footer__mark"
  }, mark), links.length > 0 && /*#__PURE__*/React.createElement("ul", {
    className: "footer__links"
  }, links.map(l => /*#__PURE__*/React.createElement("li", {
    key: l.href
  }, /*#__PURE__*/React.createElement("a", {
    href: l.href
  }, l.label)))), /*#__PURE__*/React.createElement("div", {
    className: "footer__fine"
  }, children)));
}
Object.assign(__ds_scope, { SiteFooter });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/site/SiteFooter.jsx", error: String((e && e.message) || e) }); }

__ds_ns.Button = __ds_scope.Button;

__ds_ns.MarkerCaption = __ds_scope.MarkerCaption;

__ds_ns.Notice = __ds_scope.Notice;

__ds_ns.Prose = __ds_scope.Prose;

__ds_ns.Sticker = __ds_scope.Sticker;

__ds_ns.CastGrid = __ds_scope.CastGrid;

__ds_ns.PlayTeaser = __ds_scope.PlayTeaser;

__ds_ns.QualityBox = __ds_scope.QualityBox;

__ds_ns.VideoBlock = __ds_scope.VideoBlock;

__ds_ns.Nav = __ds_scope.Nav;

__ds_ns.PageHeader = __ds_scope.PageHeader;

__ds_ns.SiteFooter = __ds_scope.SiteFooter;

})();
