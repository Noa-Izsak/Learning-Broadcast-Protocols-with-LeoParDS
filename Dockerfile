FROM python:3.9

COPY requirements.txt requirements.txt

RUN pip install pip==21.2.3
RUN pip install --upgrade cython
RUN pip install numpy==1.26.4
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /code
COPY . .