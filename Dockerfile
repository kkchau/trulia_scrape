FROM python:3.10-slim-bullseye

COPY . /opt/trulia_scrape

ENV PYTHONPATH ${PYTHONPATH}:/opt/trulia_scrape
RUN pip install -r /opt/trulia_scrape/requirements.txt

ENTRYPOINT ["python", "/opt/trulia_scrape/trulia_scrape/scrape.py"]
