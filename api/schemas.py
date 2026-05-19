from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class VisitorFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid")

    Administrative: float = Field(..., ge=0)
    Administrative_Duration: float = Field(..., ge=0)
    Informational: float = Field(..., ge=0)
    Informational_Duration: float = Field(..., ge=0)
    ProductRelated: float = Field(..., ge=0)
    ProductRelated_Duration: float = Field(..., ge=0)
    BounceRates: float = Field(..., ge=0, le=1)
    ExitRates: float = Field(..., ge=0, le=1)
    PageValues: float = Field(..., ge=0)
    SpecialDay: float = Field(..., ge=0, le=1)
    Month: str
    OperatingSystems: float
    Browser: float
    Region: float
    TrafficType: float
    VisitorType: str
    Weekend: bool


class HealthResponse(BaseModel):
    status: str
    service: str


class VersionResponse(BaseModel):
    project: str
    api_version: str
    model_path: str
    preprocessor_path: str | None
    model_is_pipeline: bool
    threshold: float


class PredictionResponse(BaseModel):
    purchase_probability: float
    prediction: int
    threshold: float
    model_path: str
