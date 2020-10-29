FROM python:3
ADD run.py /
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "./run.py"]
