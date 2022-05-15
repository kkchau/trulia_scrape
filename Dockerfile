FROM python:3.10-slim-bullseye

COPY . /opt/trulia_to_notion

ENV PYTHONPATH ${PYTHONPATH}:/opt/trulia_to_notion
RUN pip install -r /opt/trulia_to_notion/requirements.txt

ENTRYPOINT ["python", "/opt/trulia_to_notion/trulia_to_notion/main.py"]
