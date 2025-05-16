FROM node:22.15.0-alpine

WORKDIR /app

COPY . .

RUN npm install -g @angular/cli && npm install 


EXPOSE 4200

CMD ["ng", "serve", "--host", "0.0.0.0", "--proxy-config", "proxy.conf.json"]