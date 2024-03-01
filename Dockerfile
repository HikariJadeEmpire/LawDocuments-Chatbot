FROM python:3.11
WORKDIR /app

COPY ./app/LLM.py /app/LLM.py
COPY ./app/m_vector_db.py /app/m_vector_db.py
COPY ./app/main.py /app/main.py
COPY ./app/upload.py /app/upload.py
COPY requirements.txt /app/requirements.txt
# COPY ./docs_storage /docs_storage

RUN pip install --upgrade pip
RUN apt-get -y install libc-dev
RUN pip install -r requirements.txt
RUN mkdir -p /docs_storage

CMD [ "python", "main.py" ]