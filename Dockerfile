#
# Dockerfile to reverse engineer https://apply.jackfrosttower.com
#
# Joe Ammond (pugpug)
#

FROM alpine:3.10.9

# Install packages
RUN apk update && apk add alpine-baselayout alpine-keys apk-tools \
	busybox curl libc-utils nginx php7 php7-fpm php7-openssl \
	supervisor bash

# Create directories
RUN mkdir -p /wwwlog /etc/supervisor/conf.d

# Copy application pieces
COPY opt /opt
COPY html /var/www/html
COPY nginx.conf /etc/nginx
COPY php.ini /etc/php7
COPY php-fpm.conf /etc/php7
COPY www.conf /etc/php7/php-fpm.d
COPY supervisord.conf /etc/supervisor/conf.d

# Fix some directory permissions
RUN chmod 777 /var/www/html /var/www/html/images

# Expose port 80
EXPOSE 80

# Run supervisord to manage the application pieces
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
