FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive

WORKDIR /transcription-webapp

RUN apt-get -y update && apt-get install -y \
build-essential \
curl \
software-properties-common \
git \
ffmpeg \
python3.9 \
python3-pip \
&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]