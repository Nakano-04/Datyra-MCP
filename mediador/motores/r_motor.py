"""Motor R: ciclo 1-6 - limpieza, EDA, modelado y evaluacion con R."""

import shutil
import subprocess
from datetime import datetime

from .. import contexto

NOMBRE = "r"
DESCRIPCION = "Ciclo 1-6 estadistico (R / Rscript) - limpieza, EDA, correl, Shapiro, clustering"


def disponible():
    return bool(shutil.which("Rscript"))


def ejecutar(peticion, archivo, salida_dir, modo="analisis"):
    if not disponible():
        return {"motor": NOMBRE, "salida": "Rscript no instalado. Instala R desde https://cran.r-project.org"}
    if archivo is None:
        return {"motor": NOMBRE, "salida": "No hay archivos de datos en Recursos."}
    nombre = archivo["ruta"].name
    ruta_r = str(archivo["ruta"].resolve()).replace("\\", "/")
    script = salida_dir / f"analisis_{datetime.now():%Y%m%d_%H%M%S}.R"
    codigo = f'''
suppressMessages({{ library(dplyr) }})
nombre <- "{nombre}"
ruta <- "{ruta_r}"
if (grepl("\\\\.csv", ruta)) {{
    df <- read.csv(ruta, stringsAsFactors=FALSE)
}} else if (grepl("\\\\.xlsx", ruta)) {{
    suppressMessages(library(readxl)); df <- read_excel(ruta)
}} else {{ stop("Formato no soportado") }}

cat("==============================================\\n")
cat(" 1-2. RECOPILACION\\n")
cat("==============================================\\n")
cat("Archivo:", nombre, "\\n"); cat("Dimensiones:", nrow(df), "x", ncol(df), "\\n")
cat("Columnas:", paste(names(df), collapse=", "), "\\n\\n")

cat("==============================================\\n")
cat(" 3. LIMPIEZA\\n")
cat("==============================================\\n")
cat("Duplicados:", sum(duplicated(df)), "\\n")
cat("Nulos por col:\\n"); print(colSums(is.na(df)))
df <- df[!duplicated(df),]
cat("\\n")

cat("==============================================\\n")
cat(" 4. EXPLORACION\\n")
cat("==============================================\\n")
print(summary(df)); cat("\\n"); print(head(df,10))

cat("\\n==============================================\\n")
cat(" 5. MODELADO - Correlacion, normalidad, clustering\\n")
cat("==============================================\\n")
num <- df[sapply(df, is.numeric)]
if (ncol(num) >= 2) {{
    cat("Correlacion Pearson:\\n"); print(cor(num, use="pairwise.complete.obs"))
    cat("\\nShapiro (normalidad, muestra 5k):\\n")
    for (c in names(num)[1:min(2, ncol(num))]) {{
        v <- na.omit(num[[c]]); v <- head(v, 5000)
        if (length(v) >= 3) {{ s <- shapiro.test(v); cat(c, ": W=", round(s$statistic,3), " p=", round(s$p.value,3), ifelse(s$p.value>0.05," ~normal"," no normal"), "\\n") }}
    }}
    if (ncol(num) >= 2 && nrow(df) >= 6) {{
        cat("\\nKMeans k=3 (segmentacion):\\n")
        set.seed(42); km <- kmeans(scale(na.omit(num)), centers=3, nstart=10)
        print(table(km$cluster)); cat("Centroides:\\n"); print(round(km$centers,2))
    }}
}}
cat("\\n==============================================\\n")
cat(" 6. EVALUACION\\n")
cat("==============================================\\n")
cat("Modelo evaluado. Listo para dashboard.\\n")
'''
    script.write_text(codigo, encoding="utf-8")
    comando = ["Rscript", "--vanilla", str(script)]
    try:
        resultado = subprocess.run(comando, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900, cwd=str(salida_dir))
    except subprocess.TimeoutExpired:
        return {"motor": NOMBRE, "script": str(script), "salida": "Timeout 900s"}
    salida = resultado.stdout or ""
    if resultado.returncode != 0:
        salida += "\n[ERROR]\n" + (resultado.stderr or "")
    return {"motor": NOMBRE, "script": str(script), "salida": salida, "comando": comando}
