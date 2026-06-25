import logging
import argparse
import json
import time
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

# Carrega variáveis do .env (como DATABASE_URL e OPENAI_API_KEY)
load_dotenv()

from app.database import SessionLocal
from app.services.collector import coletar_camara, coletar_senado

# Configura o log para você ver o progresso no terminal
logging.basicConfig(level=logging.INFO)

def parse_args():
    parser = argparse.ArgumentParser(description="Script de Ingestão de PLs")
    parser.add_argument(
        "--mode",
        choices=["incremental", "full"],
        default="incremental",
        help="Modo de ingestão: incremental (default) ou full"
    )
    return parser.parse_args()

def executar_carga(mode: str, report_path: str = "ingestion-report.json"):
    print(f"Iniciando a carga de dados... Modo: {mode}")
    
    start_time = time.time()
    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    db = SessionLocal()
    
    total_camara = 0
    total_senado = 0
    errors = []
    status = "success"
    
    try:
        if mode == "full":
            ano = 2000
            total_camara = coletar_camara(db, ano_inicial=ano)
            print(f"Câmara finalizada! {total_camara} registros.")
            total_senado = coletar_senado(db, ano_inicial=ano)
            print(f"Senado finalizado! {total_senado} registros.")
        else: # incremental
            total_camara = coletar_camara(db, numdias=2)
            print(f"Câmara finalizada! {total_camara} registros.")
            total_senado = coletar_senado(db, numdias=2)
            print(f"Senado finalizado! {total_senado} registros.")
            
        print("Carga concluída com sucesso!")
    except Exception as e:
        status = "failure"
        errors.append(str(e))
        print(f"Ocorreu um erro durante a carga: {e}")
    finally:
        db.close()
        
    finished_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    duration_seconds = int(time.time() - start_time)
    
    report = {
        "mode": mode,
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": duration_seconds,
        "camara_count": total_camara,
        "senado_count": total_senado,
        "total_count": total_camara + total_senado,
        "errors": errors,
        "status": status
    }
    
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"Relatório gerado em {report_path}")

def carga_inicial():
    args = parse_args()
    executar_carga(args.mode)

if __name__ == "__main__":
    carga_inicial()