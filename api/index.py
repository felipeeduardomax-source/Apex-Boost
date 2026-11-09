import os
import sys

# Adiciona o diretório raiz ao path do Python para importar app e database
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

# Exporta a instância Flask para o runtime da Vercel
app = app

