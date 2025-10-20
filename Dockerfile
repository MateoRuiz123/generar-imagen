FROM python:3.10-slim

# Instala herramientas necesarias
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Agrega la clave GPG de Google Chrome y el repositorio
RUN wget -q -O /usr/share/keyrings/google-linux-signing-key.gpg https://dl-ssl.google.com/linux/linux_signing_key.pub \
    && echo "deb [signed-by=/usr/share/keyrings/google-linux-signing-key.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list

# Instala Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Descarga e instala la última versión de ChromeDriver
RUN wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip

# Establece el directorio de trabajo
WORKDIR /

# Copia archivos de configuración
COPY config.ini ./
COPY requirements.txt ./

# Instala dependencias de Python con versiones compatibles
RUN pip install --no-cache-dir -r requirements.txt

# Variables de entorno para Flask
ENV FLASK_RUN_PORT=8080
ENV FLASK_RUN_HOST=0.0.0.0

# Expone el puerto
EXPOSE 8080

# Copia el resto del proyecto
COPY . .

# Comando de inicio
CMD ["python", "./app.py"]
