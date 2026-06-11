import json
import os
import argparse
from datetime import datetime, timezone

def merge_reports(report_path: str, history_path: str, max_runs: int = 90):
    if not os.path.exists(report_path):
        print(f"Erro: Relatório {report_path} não encontrado.")
        return False

    with open(report_path, "r") as f:
        new_run = json.load(f)

    if os.path.exists(history_path):
        with open(history_path, "r") as f:
            history = json.load(f)
    else:
        history = {"runs": []}

    # Prepend new run
    history["runs"].insert(0, new_run)

    # Limit to max_runs
    history["runs"] = history["runs"][:max_runs]

    # Update timestamp
    history["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Ensure target directory exists
    os.makedirs(os.path.dirname(os.path.abspath(history_path)), exist_ok=True)

    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)

    print(f"Relatório {report_path} mesclado com sucesso em {history_path}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mescla ingestion-report.json no histórico")
    parser.add_argument("--report", required=True, help="Caminho do relatório gerado")
    parser.add_argument("--history", required=True, help="Caminho do histórico (ex: docs/ingestion/ingestion-history.json)")
    parser.add_argument("--max", type=int, default=90, help="Número máximo de execuções no histórico")
    
    args = parser.parse_args()
    merge_reports(args.report, args.history, args.max)
