Install postgres with pgvector

```
docker run -d \
  --name pgvector-db \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  -v /yourlocalfolder:/var/lib/postgresql/data \
  pgvector/pgvector:pg17
  ```

Export the google client id for authentication

```
export GOOGLE_CLIENT_ID=your-id
```

## Database creation

```
CREATE USER noctua WITH PASSWORD 'noctua';
CREATE DATABASE noctua OWNER noctua;
GRANT ALL PRIVILEGES ON DATABASE noctua TO noctua;
```