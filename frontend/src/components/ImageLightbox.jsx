import { useEffect } from "react";

export default function ImageLightbox({ src, prompt, onClose }) {
  useEffect(() => {
    function onKey(e) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = prevOverflow;
    };
  }, [onClose]);

  return (
    <div
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Post image, enlarged"
      style={{
        position: "fixed", inset: 0, zIndex: 1000,
        background: "rgba(0,0,0,0.85)",
        display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        padding: "2rem", gap: "1rem", cursor: "zoom-out",
      }}
    >
      <img
        src={src}
        alt="Post visual, enlarged"
        onClick={e => e.stopPropagation()}
        style={{
          maxWidth: "min(900px, 90vw)", maxHeight: "80vh",
          objectFit: "contain",
          borderRadius: "var(--radius)",
          border: "1px solid var(--border)",
          cursor: "default",
        }}
      />
      {prompt && (
        <div
          onClick={e => e.stopPropagation()}
          style={{
            maxWidth: "min(900px, 90vw)", fontSize: "0.8125rem",
            color: "var(--text-muted)", lineHeight: 1.5, textAlign: "center",
            cursor: "default",
          }}
        >
          {prompt}
        </div>
      )}
      <button
        onClick={onClose}
        style={{
          position: "absolute", top: "1.25rem", right: "1.5rem",
          padding: "0.5rem 0.875rem", borderRadius: "var(--radius)",
          background: "var(--surface)", border: "1px solid var(--border)",
          color: "var(--text-muted)", fontSize: "0.8125rem", cursor: "pointer",
        }}
      >
        ✕ Close (Esc)
      </button>
    </div>
  );
}
