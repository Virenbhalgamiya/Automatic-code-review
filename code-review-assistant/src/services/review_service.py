from typing import List
from src.engine.analyzer import analyze_code
from src.database.connection import get_db_session
from src.database.repository import create_scan_record, get_all_scan_records
from src.api.schemas import ScanReport

class ReviewService:
    @staticmethod
    def analyze_file(filename: str, file_content: str) -> ScanReport:
        """
        Orchestrates the entire code review scan:
        1. Invokes the static analysis engine.
        2. Formats and saves the scan report to the database.
        3. Returns the scan result parsed as a Pydantic ScanReport.
        """
        # Step 1: Run static analysis
        issues = analyze_code(file_content)
        serialized_issues = [issue.model_dump() for issue in issues]
        
        # Step 2: Persist the scan in PostgreSQL
        with get_db_session() as session:
            db_record = create_scan_record(
                session=session,
                filename=filename,
                total_issues=len(issues),
                issues=serialized_issues
            )
            # Step 3: Map to Pydantic schema while inside the session (or since expire_on_commit=False, safe to map)
            report = ScanReport.model_validate(db_record)
            
        return report

    @staticmethod
    def get_all_scans() -> List[ScanReport]:
        """Retrieves all historical scans from the database, ordered by timestamp descending."""
        with get_db_session() as session:
            db_records = get_all_scan_records(session)
            # Map database records to Pydantic models
            reports = [ScanReport.model_validate(record) for record in db_records]
        return reports
