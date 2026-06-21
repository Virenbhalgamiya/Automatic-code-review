from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from src.database.models import ScanRecord
from src.database.connection import DatabaseError

def create_scan_record(session: Session, filename: str, total_issues: int, issues: List[Dict[str, Any]]) -> ScanRecord:
    """Inserts a new scan record into the database."""
    try:
        scan_record = ScanRecord(
            filename=filename,
            total_issues=total_issues,
            issues=issues
        )
        session.add(scan_record)
        session.flush()  # Flushes changes to database to get IDs and timestamps
        return scan_record
    except (OperationalError, SQLAlchemyError) as e:
        raise DatabaseError(f"Failed to save scan record to database: {str(e)}") from e

def get_all_scan_records(session: Session) -> List[ScanRecord]:
    """Retrieves all scan records from the database ordered by timestamp descending."""
    try:
        return session.query(ScanRecord).order_by(ScanRecord.timestamp.desc()).all()
    except (OperationalError, SQLAlchemyError) as e:
        raise DatabaseError(f"Failed to retrieve scan records from database: {str(e)}") from e
