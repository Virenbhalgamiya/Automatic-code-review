import os
from collections import Counter
from fastapi.testclient import TestClient
from sqlalchemy import text
from src.main_api import app
from src.database.connection import engine, init_db

def test_functional_end_to_end() -> None:
    # Ensure tables exist
    init_db()

    # Clean the test database table before starting
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE scan_records RESTART IDENTITY CASCADE"))
        conn.commit()

    client = TestClient(app)
    
    # Locate the sample file relative to this test file
    sample_file_path = os.path.join(os.path.dirname(__file__), "../sample_code.py")
    assert os.path.exists(sample_file_path), f"Sample file not found at {sample_file_path}"
    
    # 1. Perform POST /analyze upload
    filename = "sample_code.py"
    with open(sample_file_path, "rb") as f:
        response = client.post(
            "/analyze",
            files={"file": (filename, f, "text/plain")}
        )
    
    # Assert HTTP 200
    assert response.status_code == 200, f"Analysis failed: {response.text}"
    
    data = response.json()
    
    # Assert return fields
    assert data["filename"] == filename
    assert "timestamp" in data
    
    total_issues = data["total_issues"]
    issues = data["issues"]
    
    # Assert total_issues >= 6
    assert total_issues >= 6, f"Expected at least 6 issues, found {total_issues}"
    
    # Count issue types
    issue_types = [issue["issue_type"] for issue in issues]
    counts = Counter(issue_types)
    
    # Assert all 6 issue types are present
    required_types = [
        "unused_import",
        "long_function",
        "missing_docstring",
        "hardcoded_secret",
        "bare_except",
        "missing_type_hint"
    ]
    for req_type in required_types:
        assert req_type in counts, f"Missing required issue type: {req_type}"
        assert counts[req_type] >= 1, f"Expected at least 1 issue of type {req_type}"

    # 2. Call GET /scans and verify persistence
    scans_response = client.get("/scans")
    assert scans_response.status_code == 200
    scans_data = scans_response.json()
    
    # Assert the record is persisted
    db_saved = len(scans_data) > 0
    assert db_saved, "No scan records were returned from /scans"
    
    # Retrieve the saved scan detail
    saved_scan = scans_data[0]
    assert saved_scan["filename"] == filename
    assert saved_scan["total_issues"] == total_issues

    # 3. Print the exact requested summary format
    print("\n" + "=" * 31)
    print("=== FUNCTIONAL TEST RESULTS ===")
    print(f"File analyzed: {filename}")
    print(f"Total issues found: {total_issues}")
    print("Issue breakdown:")
    print(f"  - unused_import:      {counts['unused_import']}")
    print(f"  - long_function:      {counts['long_function']}")
    print(f"  - missing_docstring:  {counts['missing_docstring']}")
    print(f"  - hardcoded_secret:   {counts['hardcoded_secret']}")
    print(f"  - bare_except:        {counts['bare_except']}")
    print(f"  - missing_type_hint:  {counts['missing_type_hint']}")
    print(f"Database record saved: {'YES' if db_saved else 'NO'}")
    print(f"GET /scans returned {len(scans_data)} total records")
    print("=" * 32)
