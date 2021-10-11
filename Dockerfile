FROM python:3.8

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt

COPY ./main.py /usr/local/bin/drone-matrix

ENTRYPOINT ["python", "-u", "/usr/local/bin/drone-matrix"]
