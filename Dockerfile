FROM node:12-alpine
WORKDIR /app
COPY . .
RUN ls /app
