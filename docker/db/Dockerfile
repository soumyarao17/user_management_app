FROM mysql:8

COPY docker/db/database.sql /docker-entrypoint-initdb.d/database.sql

ENV MYSQL_ALLOW_EMPTY_PASSWORD TRUE

EXPOSE 3306