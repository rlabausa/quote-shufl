# quote-shufl
This is a simple project to help familiarize myself with PostgreSQL as a RDBMS and marks my entry point to the world of Databases. The core function of this program is to pull a random quote stored in a DB and display it to the currently logged in user.

## Project Versions
- [x] v1: basic command-line application
- [ ] v2: GUI application (with CRUD functionality) built with [Flask](https://flask.palletsprojects.com/en/1.1.x/) and [Materialize](https://materializecss.com/) frameworks
 
## Database Design
### Entity Relationship Diagram (ERD)
![er-diagram](img/quote-shufl-erd.png)

### Schema
```SQL
CREATE TABLE quote (
  id serial,
  body text,
  source varchar(40),
  PRIMARY KEY (id)
);

CREATE TABLE tag (
  id serial,
  name varchar(40) UNIQUE,
  PRIMARY KEY (id)
);

CREATE TABLE quote_tag (
  quote_id int,
  tag_id int,
  PRIMARY KEY (quote_id, tag_id),
  FOREIGN KEY(quote_id) REFERENCES quote(id),
  FOREIGN KEY (tag_id) REFERENCES tag(id)
);
```
## Bulk-Loading the Data
The data set used in this project can be found in `/data` in the root of the project directory. Data can be loaded into a database in `psql` using the `COPY` command like so:
```SQL
COPY quote(body, source) FROM '</path/to/csv/file>' WITH (FORMAT CSV, HEADER TRUE);
```

## Common Issues
### Permission Denied
If you encounter a `permission denied for table` message, ensure you have granted privilege to your database user. Using the  `GRANT` command, from the psql terminal, run the following SQL command:
```SQL
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO testuser;
```
