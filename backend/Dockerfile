FROM python:3-alpine

# Imagemagick install
ENV MAGICK_HOME=/usr
RUN apk add --no-cache imagemagick && \
apk add --no-cache imagemagick-dev

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt


# Copy all app source
COPY . .

EXPOSE 8000
VOLUME ["/opt/site/images", "/opt/site/cache"]

CMD ["python", "app.py"]
