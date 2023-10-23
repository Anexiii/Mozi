# Autoinstalación de Bibliotecas
import subprocess

# Lista de bibliotecas requeridas con versiones específicas
required_libraries = [
    {"name": "Flask", "version": "3.0.0"},
    {"name": "flask-cors", "version": "4.0.0"},
    {"name": "unidecode", "version": "1.2.0"},
    {"name": "speedtest-cli", "version": "2.1.3"},
]

# Obtener las bibliotecas instaladas actualmente
installed_libraries = subprocess.check_output(["pip", "freeze"]).decode().splitlines()

# Instalar las bibliotecas requeridas si no están instaladas
for library in required_libraries:
    if f"{library['name']}=={library['version']}" not in installed_libraries:
        subprocess.call(["pip", "install", f"{library['name']}=={library['version']}"])


# Importar las bibliotecas necesarias para el proyecto
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from unidecode import unidecode
import speedtest
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import string


# Configuración de Flask y lectura del archivo JSON
app = Flask(__name__)
CORS(app)

ruta_json = r".\intents.json"

with open(ruta_json, "r", encoding="utf-8") as archivo_json:
    datos = json.load(archivo_json)
    intents = datos["intents"]


def preprocesar_texto(texto):
    # Eliminar puntuación y acentos, y convertir a minúsculas
    texto_sin_puntuacion = texto.translate(str.maketrans("", "", string.punctuation))
    texto_sin_acentos = unidecode(texto_sin_puntuacion)
    return texto_sin_acentos.lower()


def realizar_prueba_de_velocidad():
    # Realizar una prueba de velocidad de Internet
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = st.download() / 1_000_000  # Velocidad de descarga en Mbps
    upload_speed = st.upload() / 1_000_000  # Velocidad de carga en Mbps
    return f"Velocidad de descarga: {download_speed:.2f} Mbps\nVelocidad de carga: {upload_speed:.2f} Mbps"


def responder_pregunta(pregunta):
    pregunta = preprocesar_texto(pregunta)
    respuesta = (
        "Lo siento, no tengo respuesta para esa pregunta. ¿Puedo ayudarte con algo más?"
    )

    # Buscar respuestas de despedida
    palabras_despedida = ["chau", "adios", "hasta luego"]
    for palabra in palabras_despedida:
        if palabra in pregunta:
            respuesta = "Hasta luego. ¡Que tengas un buen día!"
            break

    for intent in intents:
        if "preguntas" in intent:
            if pregunta in intent["preguntas"]:
                # Encuentra la respuesta correspondiente a la pregunta específica
                for idx, preg in enumerate(intent["preguntas"]):
                    if pregunta == preg:
                        respuesta = intent["respuestas"][idx]
                        break
        elif "preguntas_respuestas" in intent:
            for preg_resp in intent["preguntas_respuestas"]:
                if pregunta == preprocesar_texto(preg_resp["pregunta"]):
                    respuesta = preg_resp["respuesta"]
                    break

    if pregunta == "prueba de velocidad":
        respuesta = realizar_prueba_de_velocidad()
        correo_destino_tecnico = "joaquindelgado_26@hotmail.com"
        enviar_correo_pregunta_no_respondida(correo_destino_tecnico, pregunta)

    return respuesta


def enviar_correo_pregunta_no_respondida(correo_destino, pregunta):
    smtp_server = "smtp.office365.com"
    smtp_port = 587
    smtp_username = "mozi22ipt@hotmail.com"
    smtp_password = "Mozi44200600"

    mensaje = MIMEMultipart()
    mensaje["From"] = smtp_username
    mensaje["To"] = correo_destino
    mensaje["Subject"] = "Pregunta no respondida"

    cuerpo_mensaje = f"La siguiente pregunta no pudo ser respondida:\n\n{pregunta}"
    mensaje.attach(MIMEText(cuerpo_mensaje, "plain"))

    servidor_smtp = smtplib.SMTP(smtp_server, smtp_port)
    servidor_smtp.starttls()
    servidor_smtp.login(smtp_username, smtp_password)
    servidor_smtp.sendmail(smtp_username, correo_destino, mensaje.as_string())
    servidor_smtp.quit()


@app.route("/Mozi", methods=["POST"])
def Mozi():
    data = request.get_json()
    user_message = data.get("message", "")
    respuesta = responder_pregunta(user_message)
    return jsonify({"response": respuesta})


if __name__ == "__main__":
    # Ejecutar la aplicación Flask en el servidor
    app.run(host="0.0.0.0", port=5000)


# Mantener la ventana de la consola abierta
import os

os.system("pause")
