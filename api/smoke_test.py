from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = ROOT / "handoff" / "contracts" / "c_example_request.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.main import health, predict, predict_batch, startup_event, version  # noqa: E402
from api.schemas import BatchPredictionRequest, VisitorFeatures  # noqa: E402


def main() -> None:
    startup_event()

    health_payload = health().model_dump()
    assert health_payload["status"] == "ok"

    version_payload = version().model_dump()
    for field in ["api_version", "model_version", "model_sha", "model_path", "threshold"]:
        assert field in version_payload, f"Falta {field} en /version"

    with REQUEST_PATH.open(encoding="utf-8") as file:
        request_payload = json.load(file)

    prediction_payload = predict(VisitorFeatures(**request_payload)).model_dump()
    for field in ["purchase_probability", "prediction", "threshold", "model_path", "model_version", "model_sha"]:
        assert field in prediction_payload, f"Falta {field} en /predict"

    batch_payload = predict_batch(BatchPredictionRequest(records=[VisitorFeatures(**request_payload)])).model_dump()
    assert batch_payload["count"] == 1, "predict_batch debe devolver count=1"
    assert "purchase_probability" in batch_payload["records"][0], "Falta purchase_probability en /predict_batch"

    print("Smoke test PB-19 OK")
    print(json.dumps({"version": version_payload, "prediction": prediction_payload, "batch": batch_payload}, indent=2))


if __name__ == "__main__":
    main()
