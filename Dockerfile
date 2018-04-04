# ==========+ Frontend Dependencies +==========
FROM node:9 as frontend
ENV npm_config_strict_ssl=false
RUN npm install -g vue-cli

# ` To create a vue project using vue-cli
#       vue init webpack frontend
ENV SOURCE_DIR="/usr/share/web-vue/"

# ` Install dependencies
WORKDIR ${SOURCE_DIR}
COPY ./frontend/package.json .
RUN npm install

# ` Minimize/Optimize/Compile standalone build
COPY ./frontend/ ${SOURCE_DIR}/
RUN NODE_ENV='production' npm run build

# ` Development Server
EXPOSE 8080
ENTRYPOINT [ "npm", "start"]
