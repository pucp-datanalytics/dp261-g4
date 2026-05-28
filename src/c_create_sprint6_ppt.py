from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import html


OUT = Path("reports/sprint6_rol5_evidencias.pptx")

SLIDES = [
    ("Sprint 6 - Evidencias de Deployment y Rol 5", [
        "Proyecto 2: Conversion de Visitantes Online.",
        "Objetivo: demostrar MVP desplegado en AWS, dashboard conectado a API y monitoreo operativo.",
        "Rol 5: logs, metricas, alertas, trazabilidad y runbook.",
    ], "Pegar captura: GitHub Actions en verde o dashboard AWS."),
    ("Objetivo del Sprint 6 segun el PDF", [
        "Empaquetar el modelo final como API REST.",
        "Desplegar el MVP en AWS usando Docker.",
        "Integrar el dashboard del Sprint 5 con la API desplegada.",
        "Cerrar CRISP-DM con un sistema funcional y monitoreado.",
    ], "Evidencia esperada: API, dashboard, contenedores, logs y CloudWatch."),
    ("Arquitectura desplegada", [
        "Usuario accede al dashboard Streamlit en EC2 por puerto 8080.",
        "Dashboard consume la API FastAPI en la red Docker: http://sprint6-api:8000.",
        "API carga el modelo final XGBoost desde handoff/model/c_final_model.pkl.",
        "API devuelve probabilidad, clase predicha, version y hash del modelo.",
    ], "Pegar captura: dashboard con API disponible."),
    ("GitHub Actions / CI-CD", [
        "Workflow Deploy MVP ejecutado sobre feat/PB-review3.",
        "Commit validado: a8aaebf Deploy Sprint 6 API with dashboard.",
        "Construye dos imagenes Docker: dashboard y API.",
        "Despliega ambos contenedores en EC2.",
    ], "Pegar captura: GitHub Actions en verde."),
    ("Docker en EC2", [
        "Contenedor dp261-g4: dashboard Streamlit en puerto 8080.",
        "Contenedor sprint6-api: API FastAPI en puerto 8000.",
        "La API aparece healthy, validando healthcheck del contenedor.",
        "Ambos corren en la misma instancia EC2.",
    ], "Pegar captura: sudo docker ps con dp261-g4 y sprint6-api."),
    ("Endpoints de la API", [
        "GET /health devuelve status ok.",
        "GET /version devuelve project, api_version, model_version y model_sha.",
        "POST /predict devuelve purchase_probability y prediction.",
        "POST /predict_batch permite validar datasets cargados desde dashboard.",
    ], "Pegar captura: curl /health y /version."),
    ("Prediccion real desde la API", [
        "Se envio un JSON compatible con handoff/contracts/c_example_request.json.",
        "La API respondio con purchase_probability = 0.0146041093.",
        "La clase predicha fue prediction = 0 con threshold = 0.5.",
        "La respuesta incluye model_version = c_final_model y model_sha = 8f55f14ec7b1.",
    ], "Pegar captura: curl POST /predict y respuesta JSON."),
    ("Rol 5 - Logs estructurados JSON", [
        "La API emite logs JSON por stdout.",
        "Campos observados: event, endpoint, method, status_code, latency_ms, request_id.",
        "Para predicciones agrega proba, prediction, threshold, model_version y model_sha.",
        "Estos campos permiten monitoreo y trazabilidad operativa.",
    ], "Pegar captura: sudo docker logs sprint6-api con event predict."),
    ("Rol 5 - Metricas derivables", [
        "Latencia p50/p95/p99: calculable con latency_ms.",
        "Throughput: conteo de event=request o event=predict por ventana.",
        "Error rate 5xx: filtro status_code >= 500.",
        "Drift operativo: distribucion de proba y prediction en el tiempo.",
    ], "Archivo de soporte: monitoring/cloudwatch-log-insights.md."),
    ("CloudWatch y alarmas", [
        "Existe alarma CloudWatch dp261-g4-cpu-high sobre CPUUtilization.",
        "Estado observado: CORRECTO.",
        "El repo incluye alarmas sugeridas para API: error 5xx, latencia p95 y throughput.",
        "Archivo de soporte: monitoring/cloudwatch-alarms.json.",
    ], "Pegar captura: alarma CPU en CloudWatch."),
    ("Runbook operativo", [
        "El runbook explica como validar /health, /version y /predict.",
        "Incluye comandos para revisar logs y reiniciar contenedores.",
        "Documenta riesgos de AWS Academy: IP y credenciales temporales.",
        "Archivo: docs/runbook.md.",
    ], "Pegar captura o mencionar ruta del runbook en GitHub."),
    ("Manejo de IP y credenciales variables", [
        "AWS Academy puede cambiar IP publica, access key, secret y session token.",
        "La solucion es actualizar GitHub Secrets, no modificar codigo.",
        "El dashboard se conecta internamente a la API con http://sprint6-api:8000.",
        "Solo cambia la URL publica de acceso al dashboard: http://NUEVA_IP:8080.",
    ], "Pegar captura: AWS Academy / EC2 con nueva IP publica."),
    ("Checklist de cierre Sprint 6", [
        "GitHub Actions en verde.",
        "EC2 con dos contenedores activos: dashboard y API.",
        "/health, /version y /predict funcionando.",
        "Dashboard muestra API disponible y realiza predicciones.",
        "Logs JSON de prediccion disponibles.",
        "CloudWatch CPU alarm y runbook documentados.",
    ], "Archivo de soporte: docs/sprint6_completion_checklist.md."),
    ("Conclusion ejecutiva", [
        "El MVP esta desplegado y funcional en AWS.",
        "El dashboard consume predicciones en vivo desde la API REST.",
        "La API usa el modelo final XGBoost versionado y trazable.",
        "Rol 5 queda cubierto con logs JSON, CloudWatch CPU, consultas, alarmas sugeridas y runbook.",
        "El sistema queda listo para demo y para iteraciones futuras.",
    ], "Cierre: mostrar dashboard y prediccion en vivo."),
]


def escape(text: str) -> str:
    return html.escape(text, quote=True)


def text_body(lines: list[tuple[str, bool]], size: int = 1900, color: str = "111827") -> str:
    paragraphs = []
    for text, bold in lines:
        paragraphs.append(
            f'<a:p><a:r><a:rPr lang="es-PE" sz="{size}" b="{str(bold).lower()}">'
            f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:rPr>'
            f"<a:t>{escape(text)}</a:t></a:r></a:p>"
        )
    return '<p:txBody><a:bodyPr wrap="square"/><a:lstStyle/>' + "".join(paragraphs) + "</p:txBody>"


def shape(idx: int, x: int, y: int, cx: int, cy: int, lines: list[tuple[str, bool]], fill: str, line: str, size: int, color: str) -> str:
    return f"""
    <p:sp>
      <p:nvSpPr><p:cNvPr id="{idx}" name="Box {idx}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
      <p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
      <a:prstGeom prst="roundRect"><a:avLst/></a:prstGeom>
      <a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>
      <a:ln w="12700"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln></p:spPr>
      {text_body(lines, size, color)}
    </p:sp>"""


def slide_xml(title: str, bullets: list[str], evidence: str) -> str:
    bullet_lines = [(f"- {item}", False) for item in bullets]
    shapes = [
        shape(2, 420000, 250000, 9200000, 620000, [(title, True)], "FFFFFF", "FFFFFF", 3200, "111827"),
        shape(3, 560000, 1050000, 6100000, 3500000, bullet_lines, "F8FAFC", "CBD5E1", 1850, "111827"),
        shape(4, 7000000, 1050000, 2600000, 3500000, [("Evidencia", True), (evidence, False), ("Espacio para captura", True)], "EFF6FF", "93C5FD", 1650, "1E3A8A"),
        shape(5, 560000, 5050000, 9000000, 410000, [("Sprint 6 | Deployment MVP | API + AWS + Dashboard + Monitoring", False)], "111827", "111827", 1400, "FFFFFF"),
    ]
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    {''.join(shapes)}
  </p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''


def build() -> None:
    OUT.parent.mkdir(exist_ok=True)
    content = ['''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>''']
    for i in range(1, len(SLIDES) + 1):
        content.append(f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
    content.append("</Types>")

    rels = ['''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">''']
    for i in range(1, len(SLIDES) + 1):
        rels.append(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>')
    rels.append(f'<Relationship Id="rId{len(SLIDES)+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/></Relationships>')

    slide_ids = "".join(f'<p:sldId id="{255+i}" r:id="rId{i}"/>' for i in range(1, len(SLIDES) + 1))
    presentation = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId{len(SLIDES)+1}"/></p:sldMasterIdLst>
<p:sldIdLst>{slide_ids}</p:sldIdLst><p:sldSz cx="10058400" cy="5669280" type="wide"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>'''

    master = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/><p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst></p:sldMaster>'''
    layout = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'''
    theme = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Sprint6Theme"><a:themeElements><a:clrScheme name="Office"><a:dk1><a:srgbClr val="111827"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="1F2937"/></a:dk2><a:lt2><a:srgbClr val="F8FAFC"/></a:lt2><a:accent1><a:srgbClr val="2563EB"/></a:accent1><a:accent2><a:srgbClr val="16A34A"/></a:accent2><a:accent3><a:srgbClr val="F59E0B"/></a:accent3><a:accent4><a:srgbClr val="EF4444"/></a:accent4><a:accent5><a:srgbClr val="64748B"/></a:accent5><a:accent6><a:srgbClr val="0F766E"/></a:accent6><a:hlink><a:srgbClr val="2563EB"/></a:hlink><a:folHlink><a:srgbClr val="7C3AED"/></a:folHlink></a:clrScheme><a:fontScheme name="Office"><a:majorFont><a:latin typeface="Aptos Display"/></a:majorFont><a:minorFont><a:latin typeface="Aptos"/></a:minorFont></a:fontScheme><a:fmtScheme name="Office"><a:fillStyleLst/><a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme></a:themeElements></a:theme>'''

    with ZipFile(OUT, "w", ZIP_DEFLATED) as ppt:
        ppt.writestr("[Content_Types].xml", "".join(content))
        ppt.writestr("_rels/.rels", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/></Relationships>''')
        ppt.writestr("ppt/presentation.xml", presentation)
        ppt.writestr("ppt/_rels/presentation.xml.rels", "".join(rels))
        ppt.writestr("ppt/slideMasters/slideMaster1.xml", master)
        ppt.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>''')
        ppt.writestr("ppt/slideLayouts/slideLayout1.xml", layout)
        ppt.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>''')
        ppt.writestr("ppt/theme/theme1.xml", theme)
        for i, (title, bullets, evidence) in enumerate(SLIDES, 1):
            ppt.writestr(f"ppt/slides/slide{i}.xml", slide_xml(title, bullets, evidence))
            ppt.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>''')


if __name__ == "__main__":
    build()
    print(OUT)
