
FROM python:3

ADD main.py /
COPY resources/tweets.txt /resources/

RUN pip install pystrich

CMD [ "python", "./main.py" ]



