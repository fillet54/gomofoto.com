
docker run -d \
	-p 8001:8000 \
	-v /home/phillip/images:/opt/site/images \
	-v /home/phillip/image_cache:/opt/site/cache \
	site-backend
