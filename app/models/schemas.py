from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum


class ProcessingStatus(str, Enum):
    OK = "ok"
    ERROR = "error"
    UNPROCESSED = "unprocessed"


class TestStatus(str, Enum):
    LOW = "low"
    HIGH = "high"
    NORMAL = "normal"
    CRITICAL = "critical"


class ReferenceRange(BaseModel):
    low: float
    high: float


class NormalizedTest(BaseModel):
    name: str
    value: float
    unit: str
    status: TestStatus
    ref_range: ReferenceRange


class OCRResult(BaseModel):
    tests_raw: List[str]
    confidence: float


class NormalizationResult(BaseModel):
    tests: List[NormalizedTest]
    normalization_confidence: float


class PatientFriendlySummary(BaseModel):
    summary: str
    explanations: List[str]


class FinalOutput(BaseModel):
    tests: List[NormalizedTest]
    summary: str
    status: ProcessingStatus
    explanations: List[str] = Field(default_factory=list)
    reason: Optional[str] = None


class ErrorResponse(BaseModel):
    status: ProcessingStatus
    reason: str


class TextInput(BaseModel):
    text: str


class ProcessingResponse(BaseModel):
    result: Union[FinalOutput, ErrorResponse]
