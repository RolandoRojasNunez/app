import os
from pathlib import Path
from flask import Flask

def base_path():
    # Retorna el directorio de trabajo actual
    return os.path.dirname(os.path.realpath(__file__))

def app_path():
    # Para este caso, asumiremos que 'app' es un directorio en el directorio de trabajo actual
    return Path(base_path()) / 'app'

def public_path():
    # Para este caso, asumiremos que 'public' es un directorio en el directorio de trabajo actual
    return Path(base_path()) / 'static' / 'public'

def registro_path():
    # Para este caso, asumiremos que 'public' es un directorio en el directorio de trabajo actual
    return Path(base_path()) / 'static' / 'registro'