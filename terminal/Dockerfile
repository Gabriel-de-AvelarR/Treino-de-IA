FROM node:22.15.0

WORKDIR /app

COPY . .

RUN npm cache clean --force
RUN npm install -g @angular/cli && npm install 
RUN ls -la && cat angular.json


EXPOSE 4200

CMD ["ng", "serve", "--host", "0.0.0.0", "--proxy-config", "proxy.conf.json"]