FROM python:3.11-slim
WORKDIR /opt/dnsmule
RUN useradd -M dnsmule
COPY . ./
RUN chown -R root:dnsmule . && chmod -R 770 .
USER dnsmule
RUN python -m venv venv \
    && venv/bin/python -m pip install --no-cache-dir --upgrade pip \
    && venv/bin/python -m pip install --no-cache-dir .[redis] ./plugins[all] \
    && venv/bin/python -m pip install --no-cache-dir -r server/requirements.txt
RUN cp rules/rules.yml rules/rules-old.yml  \
    && sed -e 's/host: 127.0.0.1/host: redis/g' rules/rules-old.yml > rules/rules.yml
EXPOSE 8080
ENTRYPOINT ["venv/bin/python", "-m", "uvicorn", "--host", "0.0.0.0", "--port", "8080", "server.server:app"]