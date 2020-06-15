FROM python:3.7
RUN pip install pipenv
ADD *.py /
ADD Pipfile* /
RUN pipenv lock --requirements > /requirements.txt
RUN pip install -r /requirements.txt

CMD python3 /entrypoint.py
