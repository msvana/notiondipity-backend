FROM flyio/postgres-flex:15.2

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        postgresql-server-dev-15

# Set the pgvector version
ARG PGVECTOR_VERSION=0.5.1

# Download and extract the pgvector release, build the extension, and install it
RUN curl -L -o pgvector.tar.gz "https://github.com/ankane/pgvector/archive/refs/tags/v${PGVECTOR_VERSION}.tar.gz" && \
    tar -xzf pgvector.tar.gz && \
    cd "pgvector-${PGVECTOR_VERSION}" && \
    make && \
    make install

# Clean up build dependencies and temporary files
RUN apt-get remove -y build-essential curl postgresql-server-dev-all && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /pgvector.tar.gz /pgvector-${PGVECTOR_VERSION}

