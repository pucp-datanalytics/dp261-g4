from __future__ import annotations

import pandas as pd


def classify_intention(probability: float) -> tuple[str, str, str]:
    if probability >= 0.70:
        return "Alta", "Priorizar cupón, chat u oferta personalizada.", "success"
    if probability >= 0.35:
        return "Media", "Mostrar recomendaciones de productos o recordatorio.", "warning"
    return "Baja", "Mantener navegación normal y considerar retargeting posterior.", "info"


def performance_status(validation: pd.DataFrame) -> tuple[str, str]:
    if validation.empty:
        return "Amarillo", "No se encontró comparación train/CV/test. Revisar artefactos de validación."
    final_test = validation[validation["phase"].eq("final_test_threshold_0_5")]
    final_train = validation[validation["phase"].eq("final_train_threshold_0_5")]
    if final_test.empty or final_train.empty:
        return "Amarillo", "La validación existe, pero no contiene las filas finales esperadas."
    train_f1 = float(final_train.iloc[0]["f1"])
    test_f1 = float(final_test.iloc[0]["f1"])
    gap = train_f1 - test_f1
    if test_f1 < 0.60 or gap > 0.15:
        return "Rojo", "Riesgo alto: revisar overfitting, umbral y estabilidad antes de usar en negocio."
    if gap > 0.08:
        return "Amarillo", "Desempeño aceptable, con brecha train-test a monitorear."
    return "Verde", "Desempeño coherente entre train y test. Apto para prototipo ejecutivo."


def executive_summary(kpis: dict) -> dict:
    threshold = kpis.get("recommended_threshold", 0.5)
    expected_value = kpis.get("expected_value", 0.0)
    recall = kpis.get("recall", 0.0)
    precision = kpis.get("precision", 0.0)
    return {
        "meaning": (
            f"El modelo detecta visitantes con intención de compra con recall de {recall:.1%} "
            f"y precision de {precision:.1%}, priorizando oportunidades comerciales sobre sesiones de mayor valor."
        ),
        "action": (
            f"Usar el umbral de negocio {threshold:.2f} para activar incentivos focalizados. "
            "Evitar descuentos masivos indiscriminados."
        ),
        "risk": "Monitorear drift, estacionalidad y cambios en campañas, porque el comportamiento online cambia con rapidez.",
        "confidence": (
            f"Bajo los supuestos actuales, el valor esperado estimado es {expected_value:,.0f}. "
            "Debe validarse con costos reales antes de producción."
        ),
    }


def business_recommendations() -> list[str]:
    return [
        "Priorizar incentivos en visitantes con alta probabilidad de compra.",
        "No ofrecer descuentos indiscriminadamente: reservarlos para sesiones con mayor intención.",
        "Ajustar el threshold según el costo real de campañas y margen promedio.",
        "Usar el valor estimado de páginas y el tiempo en páginas de producto como señales de intención.",
        "Monitorear conversión por mes, tipo de visitante y fin de semana.",
        "Preparar una API en Sprint 6 para evaluación en tiempo real.",
        "Medir resultados reales después de aplicar acciones comerciales.",
    ]
