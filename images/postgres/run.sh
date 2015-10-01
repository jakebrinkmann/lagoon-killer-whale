#!/usr/bin/env bash
docker rm espa-postgres-instance
docker run -it -p 5432:5432 -e ENCODING=UTF8  --name espa-postgres-instance espa-db
