"""
Utilidades de tuning para el Sprint 4.

Este módulo centraliza funciones reutilizables para:
- Ejecutar búsquedas de hiperparámetros con GridSearchCV.
- Ejecutar búsquedas de hiperparámetros con RandomizedSearchCV.
- Medir tiempo de ejecución.
- Guardar el mejor modelo encontrado.
- Validar que un modelo guardado pueda cargarse y predecir.

Estas funciones sirven como soporte del rol Experiment Tracker.
"""

import time
from typing import Any, Dict, Optional, Tuple

import joblib
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV


def tune_model_grid(
    model: Any,
    param_grid: Dict[str, Any],
    X: Any,
    y: Any,
    cv: Any,
    scoring: str = "f1",
    n_jobs: int = -1,
    verbose: int = 1,
    model_name: str = "model",
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Ejecuta GridSearchCV para optimizar hiperparámetros.

    Parameters
    ----------
    model:
        Modelo base de scikit-learn o compatible.
    param_grid:
        Diccionario con la grilla de hiperparámetros.
    X:
        Variables predictoras.
    y:
        Variable objetivo.
    cv:
        Estrategia de validación cruzada.
    scoring:
        Métrica principal para seleccionar el mejor modelo.
    n_jobs:
        Número de procesos paralelos.
    verbose:
        Nivel de detalle durante la búsqueda.
    model_name:
        Nombre descriptivo del modelo.
    output_path:
        Ruta opcional donde se guardará el mejor modelo.

    Returns
    -------
    dict
        Resumen del experimento de tuning.
    """
    start = time.time()

    search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        scoring=scoring,
        cv=cv,
        n_jobs=n_jobs,
        verbose=verbose,
        return_train_score=True,
    )

    search.fit(X, y)

    elapsed = round(time.time() - start, 2)

    if output_path is not None:
        joblib.dump(search.best_estimator_, output_path)

    return {
        "model": model_name,
        "search_type": "GridSearchCV",
        "best_score": search.best_score_,
        "best_params": search.best_params_,
        "time_seconds": elapsed,
        "model_path": output_path,
    }


def tune_model_randomized(
    model: Any,
    param_distributions: Dict[str, Any],
    X: Any,
    y: Any,
    cv: Any,
    scoring: str = "f1",
    n_iter: int = 20,
    random_state: int = 42,
    n_jobs: int = -1,
    verbose: int = 1,
    model_name: str = "model",
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Ejecuta RandomizedSearchCV para optimizar hiperparámetros.

    Parameters
    ----------
    model:
        Modelo base de scikit-learn o compatible.
    param_distributions:
        Distribuciones o listas de hiperparámetros.
    X:
        Variables predictoras.
    y:
        Variable objetivo.
    cv:
        Estrategia de validación cruzada.
    scoring:
        Métrica principal para seleccionar el mejor modelo.
    n_iter:
        Número de combinaciones aleatorias a probar.
    random_state:
        Semilla para reproducibilidad.
    n_jobs:
        Número de procesos paralelos.
    verbose:
        Nivel de detalle durante la búsqueda.
    model_name:
        Nombre descriptivo del modelo.
    output_path:
        Ruta opcional donde se guardará el mejor modelo.

    Returns
    -------
    dict
        Resumen del experimento de tuning.
    """
    start = time.time()

    search = RandomizedSearchCV(
        estimator=model,
        param_distributions=param_distributions,
        n_iter=n_iter,
        scoring=scoring,
        cv=cv,
        n_jobs=n_jobs,
        verbose=verbose,
        random_state=random_state,
        return_train_score=True,
    )

    search.fit(X, y)

    elapsed = round(time.time() - start, 2)

    if output_path is not None:
        joblib.dump(search.best_estimator_, output_path)

    return {
        "model": model_name,
        "search_type": "RandomizedSearchCV",
        "best_score": search.best_score_,
        "best_params": search.best_params_,
        "time_seconds": elapsed,
        "model_path": output_path,
    }


def validate_saved_model(
    model_path: str,
    X_sample: Any,
) -> Tuple[Any, Any]:
    """
    Carga un modelo guardado y valida que pueda generar predicciones.

    Parameters
    ----------
    model_path:
        Ruta del modelo guardado en formato .pkl.
    X_sample:
        Muestra de variables predictoras para probar predicción.

    Returns
    -------
    tuple
        Modelo cargado y predicciones generadas.
    """
    model = joblib.load(model_path)
    predictions = model.predict(X_sample)

    return model, predictions