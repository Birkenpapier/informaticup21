FROM continuumio/miniconda3

WORKDIR /app

SHELL ["/bin/bash", "--login", "-c"]

COPY environment.yml requirements.txt ./
RUN conda env create -f environment.yml
RUN conda install --file requirements.txt
RUN conda install -c conda-forge gym
RUN conda install -c jmcmurray os
RUN pip install datetime
RUN pip install websockets
RUN pip install matplotlib
RUN conda init bash

RUN echo "conda activate myenv" > ~/.bashrc
RUN echo "Make sure flask is installed:"
RUN python -c "import flask"


COPY speed_env_luh.py .
ENTRYPOINT ["python", "speed_env_luh.py"]