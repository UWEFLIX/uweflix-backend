# Use the official NGINX image as base
FROM nginx:latest

# Copy custom configuration file from the host into the Docker image
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80 to allow outside access to our NGINX server
EXPOSE 80