FROM python:3-alpine

# Add user and group for uwsgi to run with
RUN addgroup -g 1000 -S app && \
    adduser -S -G app -u 1000 app 

# Imagemagick install
ENV MAGICK_HOME=/usr
RUN apk add --no-cache imagemagick && \
    apk add --no-cache imagemagick-dev && \
    apk add --no-cache gcc libc-dev linux-headers

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app source
COPY . .

EXPOSE 5000
VOLUME ["/opt/site/images", "/opt/site/cache"]

CMD ["uwsgi", "wsgi.ini"]
