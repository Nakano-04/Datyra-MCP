PALETA_MOD = {
    "bg": "#0a0e14",
    "card": "#151a23",
    "accent": "#00D1FF",
    "accent2": "#FF006E",
    "accent3": "#8338EC",
    "text": "#e6e8eb",
    "muted": "#8b949e",
    "grid": "#21262d",
    "success": "#00F5A0",
    "warn": "#FFBE0B",
}

MPL_STYLE = {
    "figure.facecolor": PALETA_MOD["bg"],
    "axes.facecolor": PALETA_MOD["card"],
    "axes.edgecolor": PALETA_MOD["grid"],
    "axes.labelcolor": PALETA_MOD["text"],
    "xtick.color": PALETA_MOD["muted"],
    "ytick.color": PALETA_MOD["muted"],
    "text.color": PALETA_MOD["text"],
    "grid.color": PALETA_MOD["grid"],
    "grid.alpha": 0.4,
}

COLORES = ["#00D1FF", "#FF006E", "#8338EC", "#00F5A0", "#FFBE0B", "#FB5607", "#3A86FF"]

CSS_MOD = """
*{font-family:'JetBrains Mono','Segoe UI',monospace}
body{background:#0a0e14;color:#e6e8eb;margin:0}
.header{ background:linear-gradient(135deg,#0a0e14 0%,#151a23 50%,#1a1033 100%); border-bottom:1px solid #21262d; padding:32px 40px}
.header h1{margin:0;font-size:28px;letter-spacing:-1px}
.header h1 span{color:#00D1FF}
.badge{display:inline-block;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:700;letter-spacing:0.5px}
.badge-accent{background:rgba(0,209,255,0.15);color:#00D1FF;border:1px solid rgba(0,209,255,0.3)}
.badge-success{background:rgba(0,245,160,0.15);color:#00F5A0;border:1px solid rgba(0,245,160,0.3)}
.badge-warn{background:rgba(255,190,11,0.15);color:#FFBE0B;border:1px solid rgba(255,190,11,0.3)}
.container{max-width:1100px;margin:0 auto;padding:28px 24px}
.card{background:#151a23;border:1px solid #21262d;border-radius:16px;padding:20px 22px;margin-bottom:18px}
.card h3{margin:0 0 8px 0;font-size:13px;letter-spacing:1.2px;color:#8b949e;text-transform:uppercase}
.stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.stat{background:#0a0e14;border:1px solid #21262d;border-radius:12px;padding:14px}
.stat .v{font-size:22px;font-weight:800;color:#00D1FF}
.stat .k{font-size:10px;letter-spacing:1px;color:#8b949e;text-transform:uppercase}
 pre{background:#0a0e14;border:1px solid #21262d;border-radius:12px;padding:16px;overflow:auto;font-size:12.5px;line-height:1.6;white-space:pre-wrap;word-break:break-word}
.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}
.gallery img{width:100%;border-radius:12px;border:1px solid #21262d;background:#0a0e14}
.muted{color:#8b949e;font-size:12px}
a{color:#00D1FF;text-decoration:none}
.tag{padding:2px 8px;border-radius:6px;font-size:11px;background:#21262d;color:#8b949e;border:1px solid #30363d}
"""
