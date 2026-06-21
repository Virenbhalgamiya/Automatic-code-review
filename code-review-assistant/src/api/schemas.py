from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict
from src.engine.analyzer import Issue

class ScanReport(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Unique ID of the scan record.")
    filename: str = Field(..., description="The name of the file analyzed.")
    timestamp: datetime = Field(..., description="Timestamp of when the scan was executed.")
    total_issues: int = Field(..., description="Total number of issues found.")
    issues: List[Issue] = Field(..., description="List of issues identified during static analysis.")


class HealthReport(BaseModel):
    status: str = Field(..., description="Overall status of the service (e.g. healthy/unhealthy).")
    database: str = Field(..., description="Status of the database connection (e.g. connected/disconnected).")
    error: str | None = Field(default=None, description="Descriptive error message in case of failure.")

