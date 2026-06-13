FROM pgvector/pgvector:pg18

COPY ensure-postgres-env.sh /usr/local/bin/ensure-postgres-env.sh
RUN chmod +x /usr/local/bin/ensure-postgres-env.sh

COPY initdb/01-required-extensions.sql /docker-entrypoint-initdb.d/01-required-extensions.sql

ENTRYPOINT ["/usr/local/bin/ensure-postgres-env.sh"]
CMD ["postgres"]
