-- Database: todo-list

-- DROP DATABASE IF EXISTS "todo-list";

CREATE DATABASE "todo-list"
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_United Kingdom.1252'
    LC_CTYPE = 'English_United Kingdom.1252'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;



	CREATE DATABASE todo-list;

CREATE TABLE todo (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(2048) NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
