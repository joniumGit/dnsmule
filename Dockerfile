FROM python:3.11
WORKDIR /opt/dnsmule
COPY . ./
RUN python -m pip install . ./plugins[all] && python -m pip install -r server/requirements.txt
EXPOSE 8080
ENTRYPOINT ["python", "-m", "uvicorn", "--host", "0.0.0.0", "--port", "8080", "server.server:app"]