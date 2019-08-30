# quote-shufl
This is a simple project to mark my entry into the database world and to help familiarize myself with PostgreSQL 11 as a Relational Database Management System (RDBMS). At the basic level, this program pulls a random quote stored in a DB and displays it to the currently logged in user.

## Project Versions
- [x] **v1**: basic command-line application
- [x] **v2**: crude web app (with CRUD functionality) built with [Flask](https://flask.palletsprojects.com/en/1.1.x/) and [Materialize](https://materializecss.com/) frameworks
- [ ] **v3**: improved web app (v2 but *better*):
  - CRUD operations via admin interface
  - complex queries simplified with views
  - ORM with SQLAlchemy

## Running the Program
Before you can run either of the programs, you will need to set up a Postgres database with the relations described in the [Schema](#Schema) section with some sample [data](#Bulk-Loading-The-Data). You may also want to set up a user/password to connect to the database via a connection string. 

Once you've set up the database and loaded in the data, you will need to install all the required dependencies. Change directories into the version of the project you want to run. 

From a clean Python virtual environment, run:
```
pip install -r requirements.txt
```

Depending on which version of the project you are running, you will need to set up a configuration file. `v1` reads the DB configurations (host, user, password, ports, etc.) from a **.ini** file. `v2` loads configurations as environment variables from a **.env** file. Sample configuration files can be found in the each directory.

Once your configuration file is set up, if you want to run **v1**, you simply launch the program as you would any Python program:
```
python quote-shufl.py
```

To run **v2**, assuming you have set your `FLASK_APP` environment variables in your **.env** file, run the flask command:
```
flask run
```

You should then be able to access the application through the browser at http://localhost:5000/.


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

## psql 
### Creating Users
You can create a user in psql with the `CREATE` command. For example:
```SQL
CREATE USER testuser WITH PASSWORD 'testpassword';
```
### Bulk-Loading the Data
The data set used in this project can be found in `/data` in the root of the project directory. Data can be loaded into a database in `psql` using the [`COPY`](https://www.postgresql.org/docs/11/sql-copy.html) command:
```SQL
COPY quote(body, source) FROM '/path/to/quote.csv' WITH (FORMAT CSV, HEADER TRUE);
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


