from pydantic import BaseModel


class AstronomyNetAnnotation(BaseModel):
    radius: float
    names: list[str]
    pixelx: float
    pixely: float
    vmag: float
    type: str


class GetAnnotationResult(BaseModel):
    annotations: list[AstronomyNetAnnotation]


class CalibrationResult(BaseModel):
    parity: float
    orientation: float
    pixscale: float
    radius: float
    ra: float
    dec: float


class AstronomyNetResult(BaseModel):
    calibration: CalibrationResult
    stars: list[AstronomyNetAnnotation]
