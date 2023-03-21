FROM python:3.11
RUN useradd -ms /bin/bash dnsmule
WORKDIR /opt/dnsmule
COPY . ./
RUN chown -R root:dnsmule /opt/dnsmule && find /opt/dnsmule -type d -exec chmod 770 {} +
USER dnsmule
ENV PATH=$PATH:/home/dnsmule/.local/bin
RUN pip install --upgrade pip && python -m pip install . ./plugins[all] && python -m pip install -r server/requirements.txt
EXPOSE 8080
ENTRYPOINT ["python", "-m", "uvicorn", "--host", "0.0.0.0", "--port", "8080", "server.server:app"]