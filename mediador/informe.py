import base64
from datetime import datetime
from pathlib import Path

try:
    from jinja2 import Template
    HAS_JINJA = True
except ImportError:
    HAS_JINJA = False

from .estilos import CSS_MOD

TPL = """<!doctype html><html lang="es"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>Mediador IA — Informe</title><style>{{css}}</style></head>
<body>
<div class="header">
  <h1>◈ MEDIADOR<span>_IA</span></h1>
  <p class="muted" style="margin:8px 0 12px">Mediador de Contexto IA · Análisis automático</p>
  <span class="badge badge-accent">{{clave}}</span>
  <span class="badge badge-success">{{motor}}</span>
  <span class="muted" style="margin-left:8px">{{fecha}}</span>
</div>
<div class="container">
  <div class="card">
    <h3>Petición</h3>
    <div style="font-size:15px;font-weight:600">"{{peticion}}"</div>
    <div class="muted" style="margin-top:8px">Razones: {{razones}} · Archivo: <span class="tag">{{archivo}}</span></div>
    {% if script %}<div class="muted" style="margin-top:6px">Script: <code>{{script}}</code></div>{% endif %}
  </div>

  <div class="stat-grid">
    {% for s in stats %}
    <div class="stat"><div class="v">{{s.v}}</div><div class="k">{{s.k}}</div></div>
    {% endfor %}
  </div>

  {% if imagenes %}
  <div class="card">
    <h3>Visualizaciones</h3>
    <div class="gallery">
      {% for im in imagenes %}
      <div><img src="{{im.src}}" alt="{{im.name}}"/><div class="muted" style="margin-top:6px">{{im.name}}</div></div>
      {% endfor %}
    </div>
  </div>
  {% endif %}

  <div class="card">
    <h3>Resultado</h3>
    <pre>{{salida}}</pre>
  </div>

  <div class="card">
    <h3>Contexto</h3>
    <pre>{{contexto_txt}}</pre>
  </div>
  <p class="muted" style="text-align:center;padding:12px">Generado por Mediador IA v1 · {{fecha}}</p>
</div>
</body></html>"""

def _img_to_data_uri(p: Path):
    try:
        b = p.read_bytes()
        ext = p.suffix.lower().lstrip(".") or "png"
        mime = "image/png" if ext == "png" else f"image/{ext}"
        return f"data:{mime};base64,{base64.b64encode(b).decode()}"
    except Exception:
        return None

def generar_informe_html(carpeta: Path, peticion, clave, motor, razones, archivo, salida_txt, contexto_txt, script=None, stats=None):
    imagenes = []
    for p in sorted(carpeta.glob("*.png"), key=lambda x: x.stat().st_mtime, reverse=True)[:6]:
        uri = _img_to_data_uri(p)
        if uri:
            imagenes.append({"name": p.name, "src": uri})
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_archivo = archivo["ruta"].name if archivo else "—"
    stats = stats or []
    html = TPL.replace("{{css}}", CSS_MOD).replace("{{clave}}", clave).replace("{{motor}}", motor).replace("{{fecha}}", fecha)
    if HAS_JINJA:
        html = Template(TPL).render(css=CSS_MOD, peticion=peticion, clave=clave, motor=motor, razones=", ".join(razones), archivo=nombre_archivo, script=script or "", salida=salida_txt, contexto_txt=contexto_txt, imagenes=imagenes, stats=stats, fecha=fecha)
    else:
        html = html.replace("{{peticion}}", peticion).replace("{{razones}}", ", ".join(razones)).replace("{{archivo}}", nombre_archivo).replace("{{salida}}", salida_txt).replace("{{contexto_txt}}", contexto_txt)
    out = carpeta / f"informe_{datetime.now():%Y%m%d_%H%M%S}.html"
    out.write_text(html, encoding="utf-8")
    return out
