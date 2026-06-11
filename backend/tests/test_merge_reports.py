import json
import os
from scripts.merge_reports import merge_reports

def test_merge_reports_creates_history_if_not_exists(tmp_path):
    # Setup paths
    report_file = tmp_path / "ingestion-report.json"
    history_file = tmp_path / "ingestion-history.json"
    
    # Create dummy report
    report_data = {
        "mode": "incremental",
        "started_at": "2026-06-12T03:33:00Z",
        "finished_at": "2026-06-12T03:38:42Z",
        "duration_seconds": 342,
        "camara_count": 12,
        "senado_count": 7,
        "total_count": 19,
        "errors": [],
        "status": "success"
    }
    with open(report_file, "w") as f:
        json.dump(report_data, f)
        
    # Execute
    merge_reports(str(report_file), str(history_file))
    
    # Verify history is created properly
    assert history_file.exists()
    
    with open(history_file, "r") as f:
        history = json.load(f)
        
    assert "generated_at" in history
    assert "runs" in history
    assert len(history["runs"]) == 1
    assert history["runs"][0] == report_data

def test_merge_reports_prepends_to_existing_history(tmp_path):
    # Setup paths
    report_file = tmp_path / "ingestion-report.json"
    history_file = tmp_path / "ingestion-history.json"
    
    # Create existing history
    old_run = {"mode": "incremental", "status": "success", "total_count": 10}
    history_data = {
        "generated_at": "2026-06-11T03:38:42Z",
        "runs": [old_run]
    }
    with open(history_file, "w") as f:
        json.dump(history_data, f)
        
    # Create new report
    new_run = {"mode": "incremental", "status": "success", "total_count": 20}
    with open(report_file, "w") as f:
        json.dump(new_run, f)
        
    # Execute
    merge_reports(str(report_file), str(history_file))
    
    # Verify
    with open(history_file, "r") as f:
        history = json.load(f)
        
    assert history["generated_at"] != "2026-06-11T03:38:42Z" # Should be updated
    assert len(history["runs"]) == 2
    assert history["runs"][0] == new_run
    assert history["runs"][1] == old_run
