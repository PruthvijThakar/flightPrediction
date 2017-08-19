FROM python
RUN pip install requests pandas boto3 botocore boto arrow jupyter notebook sklearn scipy
COPY ./Finals/Dockerclassify.py /
COPY ./Finals/run.sh / 
COPY ./Finals/config.json / 
ENTRYPOINT  ["bash", "run.sh"]

