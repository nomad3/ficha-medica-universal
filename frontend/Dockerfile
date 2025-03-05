FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY src ./src
COPY public ./public
COPY *.js ./

ENV REACT_APP_API_URL=http://backend:8000

CMD ["npm", "start"] 