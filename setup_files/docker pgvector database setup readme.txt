setting pgvector from docker compose file 
Note - Make Sure docker is  installed on your machine 

# Run Below Commands for setup

docker compose up -d

docker exec -it postgres-pgvector psql -U postgres -d postgres -c 'CREATE EXTENSION vector'

docker exec -it postgres-pgvector psql -U postgres -d postgres -c 'CREATE TABLE products (id SERIAL PRIMARY KEY,name VARCHAR(255),image_url VARCHAR(255),ean VARCHAR(255),brand VARCHAR(255),category VARCHAR(255),price REAL,description TEXT,embedding VECTOR(2048),name_embedding VECTOR(384));'


