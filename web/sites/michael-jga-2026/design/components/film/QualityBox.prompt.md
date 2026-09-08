Two fassungen opposed: 1080p streaming vs. 4K download.

```jsx
<QualityBox options={[
  { title: "Streaming", spec: "1080p · H.264", text: "Direkt hier abspielen.", tag: "Empfohlen", recommended: true },
  { title: "Download", spec: "4K · ca. 3 GB", text: "Für den großen Fernseher.", hint: "Braucht Leitung und Geduld.",
    action: { href: "/videos/jga-2026-4k.mp4", label: "4K herunterladen", download: true } }
]} />
```

- Exactly two options. The 4K one always carries the bandwidth hint.
