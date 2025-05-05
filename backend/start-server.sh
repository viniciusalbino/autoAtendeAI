#!/bin/bash

# Ativa o ambiente virtual
source venv/bin/activate

# Carrega variáveis do .env para o shell (garantia extra)
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Configura as variáveis de ambiente
export FLASK_APP=src.main
export FLASK_ENV=development
export PYTHONPATH=$PYTHONPATH:.

# Inicia o servidor Flask
flask run --port=5001 --host=0.0.0.0 