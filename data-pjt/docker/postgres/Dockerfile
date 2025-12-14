FROM postgres:16

RUN apt-get update \
    && apt-get install -y \
        build-essential \
        git \
        postgresql-server-dev-16 \
        cmake \
        pkg-config \
    && cd /tmp \
    && git clone --branch v0.6.0 https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install \
    && cd .. \
    && rm -rf pgvector \
    && apt-get remove -y \
        build-essential \
        git \
        postgresql-server-dev-16 \
        cmake \
        pkg-config \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add vector extension to default database
RUN echo "CREATE EXTENSION vector;" > /docker-entrypoint-initdb.d/10-init-vector.sql 