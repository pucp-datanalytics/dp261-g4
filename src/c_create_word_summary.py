from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import html


OUTPUT_PATH = Path("reports/c_resumen_final_proyecto_por_sprints.docx")


def escape(text: object) -> str:
    return html.escape(str(text), quote=False)


class WordDoc:
    def __init__(self) -> None:
        self.items: list[str] = []

    def paragraph(self, text: str = "", style: str = "Normal") -> None:
        style_xml = "" if style == "Normal" else f'<w:pStyle w:val="{style}"/>'
        self.items.append(
            f'<w:p><w:pPr>{style_xml}</w:pPr>'
            f'<w:r><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'
        )

    def bullet(self, text: str) -> None:
        self.paragraph(f"- {text}")

    def table(self, rows: list[list[str]]) -> None:
        self.items.append('<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/></w:tblPr>')
        for row_index, row in enumerate(rows):
            self.items.append("<w:tr>")
            for cell in row:
                bold = "<w:b/>" if row_index == 0 else ""
                shade = '<w:shd w:fill="D9EAF7"/>' if row_index == 0 else ""
                self.items.append(
                    f"<w:tc><w:tcPr>{shade}</w:tcPr><w:p><w:r><w:rPr>{bold}</w:rPr>"
                    f'<w:t xml:space="preserve">{escape(cell)}</w:t></w:r></w:p></w:tc>'
                )
            self.items.append("</w:tr>")
        self.items.append("</w:tbl>")

    def page_break(self) -> None:
        self.items.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    def document_xml(self) -> str:
        body = "".join(self.items)
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f"<w:body>{body}"
            '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
            '<w:pgMar w:top="1008" w:right="1008" w:bottom="1008" w:left="1008"/>'
            "</w:sectPr></w:body></w:document>"
        )


def add_bullets(doc: WordDoc, bullets: list[str]) -> None:
    for item in bullets:
        doc.bullet(item)


def build_document() -> WordDoc:
    doc = WordDoc()
    doc.paragraph("Resumen Final del Proyecto de Datos", "Title")
    doc.paragraph("Proyecto 2: Conversión de Visitantes en Compradores Online", "Subtitle")
    doc.paragraph(
        "Documento final por sprints de la reconstrucción individual en la rama feat/PB-review3. "
        "Alcance implementado: Sprint 1 a Sprint 5. Sprint 6 queda documentado como handoff para "
        "despliegue futuro, sin API, Docker, AWS ni CI/CD implementados."
    )

    doc.paragraph("Resumen ejecutivo", "Heading1")
    doc.paragraph(
        "El proyecto reconstruye una solución de Data Science para identificar visitantes de una "
        "tienda online con alta probabilidad de compra. El objetivo de negocio es aumentar la tasa "
        "de conversión mediante acciones focalizadas como descuentos, pop-ups, ofertas personalizadas "
        "o priorización de soporte. El target oficial es Revenue=True."
    )
    doc.table(
        [
            ["Elemento", "Resultado final"],
            ["Dataset", "Online Shoppers Purchasing Intention / dataset_pucp.csv"],
            ["Dimensión", "12,330 registros y 18 variables"],
            ["Target", "Revenue"],
            ["Clase positiva", "1,908 compras, equivalente a 15.47%"],
            ["Clase negativa", "10,422 no compras, equivalente a 84.53%"],
            ["Tipo de problema", "Clasificación binaria"],
            ["Modelo final", "XGBoost"],
            ["Criterio de selección", "Mayor F1-score; recall y ROC-AUC como soporte"],
            ["F1 test final", "0.6870"],
            ["ROC-AUC test final", "0.9336"],
            ["Umbral de negocio recomendado", "0.10"],
            ["Valor esperado estimado", "28,930 bajo supuestos actuales"],
        ]
    )
    doc.paragraph("Conclusión ejecutiva", "Heading2")
    doc.paragraph(
        "El modelo final tiene desempeño coherente entre entrenamiento, validación cruzada y test. "
        "Aunque el F1 no es perfecto, es defendible para un dataset desbalanceado y el ROC-AUC alto "
        "muestra buena capacidad de ordenar visitantes según intención de compra. La principal "
        "recomendación es usar el modelo como herramienta de priorización comercial."
    )
    doc.page_break()

    doc.paragraph("Sprint 1 - Business Understanding y Data Understanding", "Heading1")
    doc.paragraph("Objetivo", "Heading2")
    doc.paragraph(
        "Comprender el problema de negocio, confirmar el target, explorar el dataset oficial y "
        "documentar la calidad inicial de los datos. Se ignoró la mecánica grupal de roles y se "
        "trabajó como reconstrucción individual."
    )
    doc.paragraph("Trabajo realizado", "Heading2")
    add_bullets(
        doc,
        [
            "Se confirmó el Proyecto 2: Conversión de Visitantes en Compradores Online.",
            "Se documentó el objetivo: aumentar conversión identificando visitantes con alta probabilidad de compra.",
            "Se confirmó Revenue como target oficial y Revenue=True como clase positiva.",
            "Se revisaron nulos, tipos de datos, duplicados, estadísticas descriptivas y distribución del target.",
            "Se confirmó el desbalance: 15.47% compras frente a 84.53% no compras.",
            "Se generaron notebooks académicos para business understanding, carga de datos, EDA y prototipo.",
        ],
    )
    doc.paragraph("Insights importantes", "Heading2")
    add_bullets(
        doc,
        [
            "La tasa de compra es baja, por lo que accuracy puede dar una impresión demasiado optimista.",
            "El F1-score es una métrica adecuada porque equilibra precision y recall ante clase positiva desbalanceada.",
            "Las variables de navegación, duración, tasas de salida/rebote y valor de página son señales relevantes de intención.",
        ],
    )
    doc.paragraph("Conclusión Sprint 1", "Heading2")
    doc.paragraph(
        "El problema quedó correctamente formulado como clasificación binaria con impacto comercial directo. "
        "El entendimiento inicial justificó usar métricas sensibles al desbalance y orientar el proyecto hacia "
        "acciones de negocio, no solo hacia accuracy."
    )
    doc.page_break()

    doc.paragraph("Sprint 2 - Data Preparation", "Heading1")
    doc.paragraph("Objetivo", "Heading2")
    doc.paragraph(
        "Preparar datos de forma reproducible, evitando data leakage y dejando un pipeline que pueda reutilizarse "
        "en entrenamiento, evaluación y futuro despliegue."
    )
    doc.paragraph("Trabajo realizado", "Heading2")
    add_bullets(
        doc,
        [
            "Se copió el dataset a data/raw/c_dataset_pucp.csv manteniendo intacto el original en docs/.",
            "Se creó src/c_preprocessing.py para limpieza, transformación y feature engineering razonable.",
            "Se hizo train_test_split con stratify=y y random_state=42 antes de cualquier fit.",
            "Se usó ColumnTransformer y Pipeline para imputación, escalado y one-hot encoding.",
            "Se integró SMOTE dentro de imblearn.pipeline.Pipeline para balancear solo train.",
            "Se guardaron datasets procesados en data/processed/ y pipelines en models/c_preproc.pkl y models/c_preprocessing_pipeline.pkl.",
        ],
    )
    doc.paragraph("Insights importantes", "Heading2")
    add_bullets(
        doc,
        [
            "El paso más crítico fue evitar fit de transformadores antes del split.",
            "SMOTE solo debe vivir dentro del pipeline de entrenamiento; nunca se aplica a test.",
            "Persistir el pipeline es clave para que Sprint 6 transforme datos nuevos igual que en entrenamiento.",
        ],
    )
    doc.paragraph("Conclusión Sprint 2", "Heading2")
    doc.paragraph(
        "La preparación quedó ordenada y reproducible. El pipeline protege contra fugas de información y reduce "
        "el riesgo de que el comportamiento en producción sea distinto al comportamiento evaluado."
    )
    doc.page_break()

    doc.paragraph("Sprint 3 - Modeling Baseline", "Heading1")
    doc.paragraph("Objetivo", "Heading2")
    doc.paragraph(
        "Entrenar modelos baseline obligatorios, evaluarlos con validación cruzada estratificada y seleccionar "
        "candidatos para Sprint 4."
    )
    doc.paragraph("Modelos entrenados", "Heading2")
    add_bullets(doc, ["Logistic Regression", "Decision Tree", "Random Forest", "SVM", "KNN"])
    doc.paragraph("Resultados comparativos principales", "Heading2")
    doc.table(
        [
            ["Modelo", "CV F1 aproximado", "Lectura"],
            ["Random Forest", "0.68", "Competitivo, pero train perfecto sugiere sobreajuste."],
            ["SVM", "0.58", "Buen baseline, pero inferior a ensambles."],
            ["Logistic Regression", "0.57", "Modelo simple y explicable, desempeño moderado."],
            ["Decision Tree", "0.57", "Train perfecto, menor robustez."],
            ["KNN", "0.42", "Rendimiento bajo para este espacio de variables."],
        ]
    )
    doc.paragraph("Insights importantes", "Heading2")
    add_bullets(
        doc,
        [
            "Random Forest fue competitivo pero mostró riesgo de overfitting.",
            "Los modelos lineales dieron una referencia útil pero no capturaron toda la complejidad.",
            "KNN quedó descartado como candidato fuerte por bajo F1.",
            "La comparación permitió priorizar modelos de ensamble y boosting para Sprint 4.",
        ],
    )
    doc.paragraph("Conclusión Sprint 3", "Heading2")
    doc.paragraph(
        "Los baseline cumplieron su rol: establecer una línea de comparación y revelar que los modelos de "
        "ensamble/boosting eran candidatos naturales para mejorar F1-score."
    )
    doc.page_break()

    doc.paragraph("Sprint 4 - Modeling Avanzado, Tuning y Selección Final", "Heading1")
    doc.paragraph("Objetivo", "Heading2")
    doc.paragraph(
        "Entrenar modelos avanzados, optimizar hiperparámetros de los mejores candidatos y seleccionar el modelo "
        "final con base en F1-score."
    )
    doc.paragraph("Trabajo realizado", "Heading2")
    add_bullets(
        doc,
        [
            "Se entrenaron XGBoost y LightGBM como modelos avanzados obligatorios.",
            "Se tunearon XGBoost, LightGBM y Random Forest con scoring=f1.",
            "Se usó StratifiedKFold para robustez ante desbalance.",
            "Se persistieron modelos tuneados y el modelo final en models/c_best_model.pkl y models/c_final_model.pkl.",
            "Se guardaron c_metrics_summary.csv, c_experiments_log.csv y c_validation_test_comparison.csv.",
        ],
    )
    doc.paragraph("Validación final", "Heading2")
    doc.table(
        [
            ["Evaluación", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC"],
            ["Train final threshold 0.50", "0.9049", "0.6720", "0.7641", "0.7151", "0.9470"],
            ["Cross-validation final", "0.8973", "0.6524", "0.7352", "0.6910", "0.9305"],
            ["Test final threshold 0.50", "0.8951", "0.6445", "0.7356", "0.6870", "0.9336"],
            ["Test threshold F1 0.54", "0.8959", "0.6553", "0.7068", "0.6801", "0.9336"],
        ]
    )
    doc.paragraph("Insights importantes", "Heading2")
    add_bullets(
        doc,
        [
            "XGBoost fue seleccionado por F1-score y estabilidad entre CV y test.",
            "El F1 de test 0.6870 es muy cercano al F1 de CV 0.6910, señal de consistencia.",
            "Random Forest mostró train perfecto, por lo que se consideró menos confiable para generalizar.",
            "El threshold técnico 0.54 no mejoró test frente a 0.50; se reportó de forma transparente.",
        ],
    )
    doc.paragraph("Conclusión Sprint 4", "Heading2")
    doc.paragraph(
        "El modelo final es XGBoost. No se observa data leakage ni brecha fuerte entre validación y test. "
        "El resultado es defendible y suficientemente estable para pasar a evaluación de negocio en Sprint 5."
    )
    doc.page_break()

    doc.paragraph("Sprint 5 - Evaluation, Business Value y Dashboard Ejecutivo", "Heading1")
    doc.paragraph("Objetivo", "Heading2")
    doc.paragraph(
        "Usar el modelo final del Sprint 4, sin entrenar modelos nuevos, para evaluar valor de negocio, definir "
        "threshold operativo, generar recomendaciones y construir un dashboard ejecutivo."
    )
    doc.paragraph("Matriz costo-beneficio", "Heading2")
    doc.table(
        [
            ["Concepto", "Valor usado"],
            ["Beneficio True Positive", "100.0"],
            ["Costo False Positive", "-10.0"],
            ["Costo False Negative", "-80.0"],
            ["Beneficio/costo True Negative", "0.0"],
            ["Umbral recomendado", "0.10"],
            ["Valor esperado", "28,930.00"],
            ["Valor por sesión", "11.8517"],
        ]
    )
    doc.paragraph("Dashboard ejecutivo", "Heading2")
    add_bullets(
        doc,
        [
            "Se construyó dashboard/c_app.py con layout ejecutivo orientado a negocio.",
            "Incluye KPIs, desempeño del modelo, matriz de confusión, sensibilidad por threshold y valor esperado.",
            "Incluye simulador interactivo de visitante con etiquetas en español.",
            "Incluye análisis de segmentos, importancia de variables, recomendaciones y handoff Sprint 6.",
            "Se agregaron archivos de soporte en dashboard/ y modelos agregados c_dashboard_*.csv.",
        ],
    )
    doc.paragraph("Insights importantes", "Heading2")
    add_bullets(
        doc,
        [
            "El threshold de negocio 0.10 es menor que 0.50 porque maximiza valor esperado bajo supuestos actuales.",
            "No se recomienda dar descuentos masivos; el modelo debe focalizar acciones donde hay mayor intención.",
            "El dashboard traduce métricas técnicas a decisiones para gerencia y e-commerce.",
            "Los supuestos económicos deben validarse con costos y margen reales antes de automatizar.",
        ],
    )
    doc.paragraph("Conclusión Sprint 5", "Heading2")
    doc.paragraph(
        "El proyecto dejó de ser solo un ejercicio de modelamiento y se convirtió en una herramienta de decisión. "
        "El dashboard permite explicar qué tan bien detecta compradores, qué valor puede generar y qué acciones "
        "comerciales tomar."
    )
    doc.page_break()

    doc.paragraph("Sprint 6 - Handoff para Futuro Despliegue", "Heading1")
    doc.paragraph("Estado", "Heading2")
    doc.paragraph(
        "Sprint 6 no fue implementado. No se creó API completa, Dockerfile final, infraestructura AWS, CI/CD ni "
        "despliegue. Solo se dejaron preparados los insumos para ejecutarlo después."
    )
    doc.paragraph("Artefactos listos", "Heading2")
    add_bullets(
        doc,
        [
            "models/c_final_model.pkl y models/c_best_model.pkl",
            "models/c_preproc.pkl y models/c_preprocessing_pipeline.pkl",
            "models/c_metrics_summary.csv y models/c_validation_test_comparison.csv",
            "src/c_predict.py como referencia de inferencia local",
            "dashboard/c_app.py como prototipo ejecutivo Sprint 5",
            "handoff/c_notes_for_sprint6.md",
            "handoff/contracts/c_input_schema.json y c_output_schema.json",
            "handoff/contracts/c_example_request.json y c_example_response.json",
            "handoff/model/c_final_model.pkl y c_preprocessing_pipeline.pkl",
        ],
    )
    doc.paragraph("Inputs que se usarán en Sprint 6", "Heading2")
    doc.table(
        [
            ["Input", "Uso previsto"],
            ["Modelo final", "Cargar una vez al iniciar la futura API y usarlo para predecir probabilidad de compra."],
            ["Pipeline de preprocesamiento", "Transformar entradas nuevas con la misma lógica usada en entrenamiento."],
            ["Contratos JSON", "Definir esquema de entrada y salida para /predict."],
            ["Script c_predict.py", "Referencia funcional para trasladar inferencia a FastAPI."],
            ["Métricas finales", "Documentar versión, desempeño esperado y límites del modelo."],
            ["Dashboard y reportes", "Alinear stakeholders antes del despliegue productivo."],
            ["Supuestos de negocio", "Validar costos, beneficios y threshold operativo con negocio."],
        ]
    )
    doc.paragraph("Trabajo recomendado para Sprint 6", "Heading2")
    add_bullets(
        doc,
        [
            "Crear API FastAPI con /health, /predict y /version.",
            "Validar payloads usando contratos del handoff.",
            "Crear Dockerfile y smoke tests locales en Sprint 6, no antes.",
            "Definir arquitectura AWS según latencia, volumen y costo.",
            "Agregar monitoreo de drift, logs estructurados y versionado de modelo.",
            "Validar threshold de negocio con experimento real o A/B test.",
        ],
    )
    doc.paragraph("Conclusión Sprint 6", "Heading2")
    doc.paragraph(
        "El handoff deja el camino preparado para convertir el prototipo en un servicio, pero preserva "
        "correctamente el alcance: Sprint 6 queda pendiente de implementación."
    )
    doc.page_break()

    doc.paragraph("Conclusiones finales", "Heading1")
    add_bullets(
        doc,
        [
            "La rama feat/PB-review3 contiene una versión limpia, individual, funcional y reproducible hasta Sprint 5.",
            "El proyecto conserva docs/ como fuente oficial y usa archivos nuevos con prefijo c_.",
            "La metodología evita data leakage mediante split temprano y pipelines entrenados solo con train.",
            "El modelo final XGBoost es coherente entre train, CV y test.",
            "El dashboard ejecutivo mejora la comunicación hacia stakeholders no técnicos.",
            "Sprint 6 queda preparado con artefactos, contratos y notas de handoff, sin implementar despliegue todavía.",
        ],
    )
    return doc


def write_docx(doc: WordDoc, output_path: Path) -> None:
    output_path.parent.mkdir(exist_ok=True)
    document = doc.document_xml()
    styles = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/>'
        '<w:rPr><w:sz w:val="22"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/>'
        '<w:rPr><w:b/><w:sz w:val="36"/><w:color w:val="1F4E79"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/>'
        '<w:rPr><w:i/><w:sz w:val="26"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="Heading 1"/>'
        '<w:rPr><w:b/><w:sz w:val="30"/><w:color w:val="1F4E79"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="Heading 2"/>'
        '<w:rPr><w:b/><w:sz w:val="24"/><w:color w:val="2F75B5"/></w:rPr></w:style>'
        '<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/>'
        '<w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4" w:color="999999"/>'
        '<w:left w:val="single" w:sz="4" w:color="999999"/>'
        '<w:bottom w:val="single" w:sz="4" w:color="999999"/>'
        '<w:right w:val="single" w:sz="4" w:color="999999"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="999999"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="999999"/></w:tblBorders></w:tblPr></w:style>'
        "</w:styles>"
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        "</Types>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        "</Relationships>"
    )
    word_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'
    )
    with ZipFile(output_path, "w", ZIP_DEFLATED) as zip_file:
        zip_file.writestr("[Content_Types].xml", content_types)
        zip_file.writestr("_rels/.rels", rels)
        zip_file.writestr("word/_rels/document.xml.rels", word_rels)
        zip_file.writestr("word/document.xml", document)
        zip_file.writestr("word/styles.xml", styles)


if __name__ == "__main__":
    write_docx(build_document(), OUTPUT_PATH)
    print(f"Documento creado: {OUTPUT_PATH}")
