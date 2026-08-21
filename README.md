Install postgres with pgvector

```
docker run -d \
  --name pgvector-db \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  -v /yourlocalfolder:/var/lib/postgresql/data \
  pgvector/pgvector:pg17
  ```