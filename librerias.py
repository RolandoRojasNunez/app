# Importando  flask y algunos paquetes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, get_flashed_messages
from confiDB import Database  # Importando conexion BD
import confiDB as db
from config import config  # Importando config para login
from config import Config
from werkzeug.security import generate_password_hash
import random
import time
import json
import hashlib
import re
import shutil
import datetime

# Modelos y entities
from models.ModelUser import ModelUser
from models.entities.User import User
from models.entities.whatsapp import *

# Libreria Login

from flask_login import LoginManager, login_user, logout_user, login_required
from flask_wtf.csrf import CSRFProtect

# Subida de archivo
from werkzeug.utils import secure_filename
import os

#Notificaciones
from nuevos import verificarRegistrosSinProveedor

#Envio de correo Administradores
from models.entities.gmail import *