FROM python:3.11-slim
WORKDIR /opt/dnsmule
RUN useradd -M dnsmule
COPY . ./
RUN chown -R root:dnsmule . && chmod -R 770 .
USER dnsmule
RUN python -m venv venv \
    && venv/bin/python -m pip install --no-cache-dir --upgrade pip \
    && venv/bin/python -m pip install --no-cache-dir .[full] ./plugins[full] \
    && venv/bin/python -m pip install --no-cache-dir -r server/requirements.txt
EXPOSE 8080
ENTRYPOINT ["venv/bin/python", "-m", "uvicorn", "--host", "0.0.0.0", "--port", "8080", "server.server:app"]