CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    image_url VARCHAR(255),
    ean VARCHAR(255),
    brand VARCHAR(255),
    category VARCHAR(255),
    price REAL,
    description TEXT,
    embedding VECTOR(2048),
    name_embedding VECTOR(328)
);
