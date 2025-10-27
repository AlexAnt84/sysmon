FROM python:3.13.9-slim-trixie

RUN useradd --uid 10000 --shell /bin/bash --create-home sysmon

USER sysmon

WORKDIR sysmon/

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py", "--web"]

EXPOSE 80
