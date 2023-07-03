FROM balenalib/raspberrypi3-debian:latest

RUN apt-get update && apt-get install -y git curl gnupg

# Install PyCoral and deps

RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN apt-get update && apt-get install -y libedgetpu1-std python3-pycoral libopenjp2-7 python3 python3-pip python3-opencv

# Install Python deps
RUN pip3 install --upgrade pip setuptools wheel
RUN python3 -m pip install numpy tqdm pyyaml

COPY . /app

WORKDIR /app

CMD ["python3", "main.py"]
