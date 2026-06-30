import sys
import json
from popular_banco import parse_args, executar_carga

def test_parse_args_default_incremental(mocker):
    mocker.patch.object(sys, 'argv', ['popular_banco.py'])
    args = parse_args()
    assert args.mode == 'incremental'

def test_parse_args_full(mocker):
    mocker.patch.object(sys, 'argv', ['popular_banco.py', '--mode', 'full'])
    args = parse_args()
    assert args.mode == 'full'

def test_executar_carga_gera_relatorio(mocker, tmp_path):
    # Mock das funções de coleta
    mocker.patch('popular_banco.coletar_camara', return_value=10)
    mocker.patch('popular_banco.coletar_senado', return_value=5)
    
    # Executa a carga em modo incremental
    executar_carga('incremental', str(tmp_path / "ingestion-report.json"))
    
    # Verifica se o relatório foi criado
    report_file = tmp_path / "ingestion-report.json"
    assert report_file.exists()
    
    # Verifica o conteúdo do relatório
    with open(report_file, 'r') as f:
        report = json.load(f)
        
    assert report['mode'] == 'incremental'
    assert report['camara_count'] == 10
    assert report['senado_count'] == 5
    assert report['total_count'] == 15
    assert report['status'] == 'success'
    assert 'started_at' in report
    assert 'finished_at' in report
    assert 'duration_seconds' in report
    assert report['errors'] == []
