FROM nginx:1.27-alpine

# Set working directory inside the image
WORKDIR /usr/share/nginx/html

# Copy static site content
COPY index.html ./
# COPY README.md ./
# COPY biengioi.kmz ./
COPY lib ./lib
COPY tiles ./tiles

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Default command is provided by nginx image