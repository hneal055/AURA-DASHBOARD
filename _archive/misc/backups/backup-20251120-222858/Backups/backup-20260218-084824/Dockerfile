FROM nginx:alpine

# Copy web files to Nginx
COPY . /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Correct CMD syntax
CMD ["nginx", "-g", "daemon off;"]
