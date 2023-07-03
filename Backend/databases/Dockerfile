FROM mysql:8.0
ENV MYSQL_ROOT_PASSWORD root_pwd
ENV MYSQL_DATABASE wcm_db
COPY ./mysql/ /docker-entrypoint-initdb.d/
