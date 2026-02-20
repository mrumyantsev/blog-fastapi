#!/usr/bin/bash

docker run \
  --name 'pg-test' \
  -d \
  -p 5432:5432 \
  -e 'POSTGRES_USER=user' \
  -e 'POSTGRES_PASSWORD=1234' \
  -e 'POSTGRES_DB=blog' \
  postgres:17-alpine3.23
