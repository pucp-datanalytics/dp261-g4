from __future__ import annotations

import json
from pathlib import Path


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip().splitlines(True)}


def code(text: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": text.strip().splitlines(True)}


SETUP = """\
from pathlib import Path
import sys
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'src'))
"""


NOTEBOOKS = [
    ("c_01_business.ipynb", "Sprint 1 - Business Understanding", "Explica el Proyecto 2, objetivo de negocio, target Revenue, problema binario, F1-score e impacto esperado.", [
        code(SETUP + "\nfrom c_preprocessing import load_raw_data, TARGET_COL\ndf = load_raw_data()\nprint(df.shape)\nprint(df[TARGET_COL].value_counts(normalize=True).round(4))")
    ]),
    ("c_02_data_loading.ipynb", "Sprint 1 - Data Loading", "Carga dataset desde docs, muestra shape, columnas, tipos y confirma target Revenue.", [
        code(SETUP + "\nfrom c_preprocessing import copy_raw_dataset, load_raw_data, RAW_COPY, TARGET_COL\ncopy_raw_dataset()\ndf = load_raw_data()\nprint('copy:', RAW_COPY)\nprint(df.shape)\nprint(list(df.columns))\nprint(df.dtypes)\nprint('target ok:', TARGET_COL in df.columns)")
    ]),
    ("c_03_eda.ipynb", "Sprint 1 - EDA", "Analiza nulos, duplicados, descriptivas, distribucion del target y visualizaciones basicas.", [
        code(SETUP + "\nimport matplotlib.pyplot as plt\nfrom c_preprocessing import load_raw_data, TARGET_COL\ndf = load_raw_data()\nprint('nulos:', df.isna().sum().sum())\nprint('duplicados:', df.duplicated().sum())\nprint(df[TARGET_COL].value_counts())\nprint(df.describe(include='all').transpose().head(20))\ndf[TARGET_COL].value_counts().plot(kind='bar', title='Revenue')\nplt.show()")
    ]),
    ("c_04_prototype.ipynb", "Sprint 1 - Prototype", "Prototipo simple para explorar variables y relaciones con Revenue.", [
        code(SETUP + "\nimport matplotlib.pyplot as plt\nfrom c_preprocessing import load_raw_data\ndf = load_raw_data()\nvariable = 'PageValues'\ndf.boxplot(column=variable, by='Revenue', figsize=(7,4))\nplt.suptitle('')\nplt.show()")
    ]),
    ("c_05_data_cleaning.ipynb", "Sprint 2 - Data Cleaning", "Documenta limpieza de duplicados, tipos y target.", [
        code(SETUP + "\nfrom c_preprocessing import load_raw_data, clean_data, TARGET_COL\nraw = load_raw_data(); clean = clean_data(raw)\nprint(raw.shape, clean.shape)\nprint('duplicados eliminados:', raw.duplicated().sum())\nprint(clean.dtypes)\nprint(clean[TARGET_COL].value_counts())")
    ]),
    ("c_06_feature_eng.ipynb", "Sprint 2 - Feature Engineering", "Documenta features derivadas sin usar target ni introducir leakage.", [
        code(SETUP + "\nfrom c_preprocessing import load_raw_data, clean_data, add_features, TARGET_COL, ENGINEERED_COLS\ndf = clean_data(load_raw_data())\nX = add_features(df.drop(columns=[TARGET_COL]))\nprint(ENGINEERED_COLS)\nprint(X[ENGINEERED_COLS].describe())")
    ]),
    ("c_07_class_balance.ipynb", "Sprint 2 - Class Balance", "Justifica balanceo por desbalance y aclara SMOTE solo train.", [
        code(SETUP + "\nfrom c_preprocessing import prepare_data\nX_train, X_test, y_train, y_test = prepare_data()\nprint('train')\nprint(y_train.value_counts(normalize=True).round(4))\nprint('test')\nprint(y_test.value_counts(normalize=True).round(4))")
    ]),
    ("c_08_pipeline.ipynb", "Sprint 2 - Pipeline", "Muestra split antes de fit, ColumnTransformer, imblearn Pipeline y persistencia.", [
        code(SETUP + "\nimport joblib\nfrom sklearn.linear_model import LogisticRegression\nfrom c_preprocessing import prepare_data, build_model_pipeline\nX_train, X_test, y_train, y_test = prepare_data()\npipe = build_model_pipeline(LogisticRegression(max_iter=1000), use_smote=True)\npipe.fit(X_train, y_train)\nprint(pipe)\nprint(joblib.load('models/c_preproc.pkl'))")
    ]),
    ("c_09_baseline_models.ipynb", "Sprint 3 - Baseline Models", "Ejecuta entrenamiento baseline reproducible.", [code("!python src/c_train_baselines.py")]),
    ("c_10_evaluation.ipynb", "Sprint 3 - Evaluation", "Evalua baselines con cross-validation estratificada y metricas completas.", [
        code("import pandas as pd\nm = pd.read_csv('models/c_baseline_metrics.csv')\nm[['model','phase','cv_accuracy','cv_precision','cv_recall','cv_f1','cv_roc_auc']].sort_values('cv_f1', ascending=False)")
    ]),
    ("c_11_model_comparison.ipynb", "Sprint 3 - Model Comparison", "Ordena modelos por F1-score y selecciona candidatos para Sprint 4.", [
        code("import pandas as pd\nm = pd.read_csv('models/c_baseline_metrics.csv')\nm.sort_values(['cv_f1','cv_recall','cv_roc_auc'], ascending=False)[['model','cv_f1','cv_recall','cv_roc_auc']].head(5)")
    ]),
    ("c_12_hyperparam_tuning.ipynb", "Sprint 4 - Hyperparameter Tuning", "Ejecuta tuning con RandomizedSearchCV y scoring f1.", [code("!python src/c_tune_models.py")]),
    ("c_13_ensembles.ipynb", "Sprint 4 - Advanced Models", "Compara XGBoost y LightGBM contra baseline y tuned.", [
        code("import pandas as pd\ns = pd.read_csv('models/c_metrics_summary.csv')\ns[['model','phase','cv_f1','cv_recall','cv_roc_auc']].sort_values('cv_f1', ascending=False).head(10)")
    ]),
    ("c_14_final_validation.ipynb", "Sprint 4 - Final Validation", "Valida modelo final en test y diagnostica overfitting, underfitting y leakage.", [
        code("import pandas as pd\npd.read_csv('models/c_validation_test_comparison.csv')"),
        code("import json\nprint(json.dumps(json.load(open('models/c_best_model_metadata.json')), indent=2))")
    ]),
    ("c_15_business_value.ipynb", "Sprint 5 - Business Value", "Ejecuta Business Value, matriz costo-beneficio, sensibilidad y umbral optimo.", [
        code("!python src/c_evaluate_business_value.py"),
        code("import pandas as pd\npd.read_csv('models/c_threshold_analysis.csv').sort_values('expected_value', ascending=False).head()")
    ]),
    ("c_16_dashboard_prototype.ipynb", "Sprint 5 - Dashboard Prototype", "Explica dashboard local y comando Streamlit.", [
        code("from pathlib import Path\nprint(Path('dashboard/c_app.ipynb').read_text(encoding='utf-8')[:1200])"),
        md("Ejecutar desde la raiz: `streamlit run dashboard/c_app.ipynb`. Es prototipo local, no despliegue AWS.")
    ]),
    ("c_17_findings_report.ipynb", "Sprint 5 - Findings Report", "Resume hallazgos, recomendaciones, reportes y handoff de Sprint 6.", [
        code("from pathlib import Path\nfor p in ['reports/c_recommendations.md','reports/c_business_value_summary.md','reports/c_model_validation_report.md','handoff/c_notes_for_sprint6.md']:\n    print('\\n---', p, '---')\n    print(Path(p).read_text(encoding='utf-8')[:1000])")
    ]),
]


def build_notebook(title: str, description: str, extra_cells: list[dict]) -> dict:
    cells = [
        md(f"# {title}\n\n{description}"),
        md("Este notebook es un entregable academico. La logica principal vive en scripts reproducibles `src/c_*.py` y aqui se documenta/ejecuta el flujo con rutas relativas."),
        *extra_cells,
        md("Notas: no se implementa Sprint 6, no se usan rutas absolutas, no se incluyen credenciales y el test set solo se usa para evaluacion final cuando corresponde."),
    ]
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> None:
    out = Path("notebooks")
    out.mkdir(exist_ok=True)
    for name, title, description, cells in NOTEBOOKS:
        nb = build_notebook(title, description, cells)
        (out / name).write_text(json.dumps(nb, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Created {len(NOTEBOOKS)} notebooks")


if __name__ == "__main__":
    main()
