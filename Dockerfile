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

# ==========+ Server dependencies +==========
FROM nginx:1.12.2-alpine as wsgi
COPY --from=frontend /usr/share/web-vue/dist/ /usr/share/web-vue/dist/

# ` Nginx doesn't support environment variables; substitute them
ENV NGINX_HOST="0.0.0.0" \
    NGINX_PORT="8080"
COPY ./run/nginx.conf /etc/nginx/conf.d/mysite.template
RUN envsubst < /etc/nginx/conf.d/mysite.template > /etc/nginx/conf.d/default.conf \
    && rm /etc/nginx/conf.d/mysite.template

# ` Production Server
EXPOSE 8080
ENTRYPOINT ["nginx", "-g", "daemon off;"]
