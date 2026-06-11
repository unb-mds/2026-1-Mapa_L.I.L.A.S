import sys
import os

# Adiciona o diretório backend ao PYTHONPATH para conseguir importar 'popular_banco'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from popular_banco import executar_carga

def main():
    print("Iniciando script de carga completa local...")
    executar_carga(mode='full')

if __name__ == "__main__":
    main()
