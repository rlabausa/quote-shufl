# quote-shufl
This is a simple project to mark my entry into the Database world and to help familiarize myself with PostgreSQL as a RDBMS. At the basic level, this program pulls a random quote stored in a DB and displays it to the currently logged in user.

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
The data set used in this project can be found in `/data` in the root of the project directory. Data can be loaded into a database in `psql` using the `COPY` command:
```SQL
COPY quote(body, source) FROM '</path/to/csv/file>' WITH (FORMAT CSV, HEADER TRUE);
```

## Common Issues
### Permission Denied
If you encounter a `permission denied for table` message, check that you have granted appropriate privileges to your database user. You can use the [`GRANT`](https://www.postgresql.org/docs/11/sql-grant.html) command to control access to databases, tables, and sequences.

To grant `ALL PRIVILEGES` to a user on the database and all tables, connect to the desired database in psql and run the following SQL commands:
```SQL
GRANT ALL PRIVILEGES ON DATABASE testdb TO testuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO testuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO testuser;
```

For a least-privileges approach, adjust the commands above to look more like the following:
```SQL
GRANT CONNECT ON DATABASE testdb TO testuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO testuser;
GRANT SELECT, USAGE ON ALL SEQUENCES IN SCHEMA public TO testuser;
```


