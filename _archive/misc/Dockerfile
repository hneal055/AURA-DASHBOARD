# Choose base image based on your project
FROM node:18-alpine  # For Node.js projects
# FROM python:3.9-slim  # For Python projects
# FROM openjdk:11-jre-slim  # For Java projects

# Set working directory
WORKDIR /app

# Copy package files first (better caching)
COPY package*.json ./
RUN npm install

# Copy project files
COPY . .

# Expose port (adjust as needed)
EXPOSE 3000

# Start command
CMD ["npm", "start"]