FROM python:3.7-alpine
RUN mkdir /src
WORKDIR /src
ADD . /src
RUN mkdir /src/tmp
RUN touch /src/tmp/data.txt
RUN echo "[{\"name\":\"alejandru\",\"email\":\"alejandru@gmail.com\"},{\"name\":\"birja\",\"email\":\"birja@gmail.com\"},{\"name\":\"muchelle\",\"email\":\"muchelle@gmail.com\"},{\"name\":\"christianu\",\"email\":\"christianu@gmail.com\"},{\"name\":\"alvaru\",\"email\":\"alvaru@gmail.com\"}]" >> /src/tmp/data.txt
RUN pip install -r requirements.txt
CMD ["python", "application.py"]
EXPOSE 5000