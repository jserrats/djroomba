FROM python:3.8
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY . /app
WORKDIR /app
ENV PATH /env/bin:$PATH
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "djroomba.wsgi", "-b 0.0.0.0:8000"]
EXPOSE 8000