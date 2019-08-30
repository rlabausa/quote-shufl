import os
import json

import psycopg2
from psycopg2.extras import RealDictCursor

# TODO set up logging
# TODO add docstrings
# TODO clean up exception-handling

class PostgresDB:
    def __init__(self, db_name, db_user, db_password):
        self.conn = psycopg2.connect(cursor_factory=RealDictCursor, # rows as dicts instead of tuples
            dbname=db_name,
            user=db_user,
            password=db_password
        )
        self.cur = self.conn.cursor()
    
    def __del__(self):
        self.db_close()
    
    def __enter__(self):
        print('__enter__')
        return self
    
    def __exit__(self,exc_type, exc_val, exc_tb):
        print('__exit__')
        self.db_close()

        if exc_type:
            print(f'exc_type: {exc_type}')
            print(f'exc_value: {exc_val}')
            print(f'exc_traceback: {exc_tb}')
    
    def db_close(self):
        print('close initiated...')
        if self.cur:
            self.cur.close()
        
        if self.conn:
            self.conn.close()
    
    def db_get_tablenames(self):
        sql = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        AND table_type='BASE TABLE';
        """
        self.cur.execute(sql)
        result = self.cur.fetchall() 
        self.conn.commit()

        return result
    
    def table_get_all_colnames(self, tablename):
        sql = """
        SELECT 
            column_name
        FROM 
            information_schema.columns
        WHERE 
            table_schema = %s
        AND 
            table_name   = %s
        ;
        """
        data = ('public', tablename)

        try:
            self.cur.execute(sql, data)
            result = self.cur.fetchall()
            self.conn.commit()
            
            return result
        
        except Exception as exc:
            self.conn.rollback()
            
            return str(exc)

    def quote_delete_one(self, id):
        sql = """
        DELETE FROM
            quote
        WHERE 
            id = (%s)
        ;
        """
        try:
            self.cur.execute(sql, (id,))
            self.conn.commit()

            return

        except Exception as exc:
            self.conn.rollback()
            
            return str(exc)
            
    def quote_insert_one(self, quote, source):
        sql = """
            INSERT INTO 
                quote(body, source)
            VALUES 
                (%s, %s)
            ;
        """
        data = (quote, source)
        try:
            self.cur.execute(sql, data)
            self.conn.commit()

            return 

        except Exception as exc:
            self.conn.rollback()

            return str(exc)
 
    def quote_select_all(self):
        sql = """
            SELECT 
                id,
                body, 
                source
            FROM 
                quote
            ;
        """
        try:
            self.cur.execute(sql)
            result = self.cur.fetchall()
            self.conn.commit()
        
            return result

        except Exception as exc:
            self.conn.rollback()

            return str(exc)
    
    def quote_select_by_id(self, id):
        sql = """
            SELECT 
                body,
                source
            FROM 
                quote
            WHERE 
                id = (%s)
            ;
        """
        data = (id,)

        try:
            self.cur.execute(sql, data)
        
            result = self.cur.fetchone()
            self.conn.commit()
            
            return result

        except Exception as exc:
            self.conn.rollback()
            
            return str(exc)

    def quote_select_random(self):
        sql ="""
                SELECT 
                    body,
                    source
                FROM 
                    quote
                OFFSET 
                    floor(random() * (SELECT COUNT(id) FROM quote))
                LIMIT 1
                ;
            """

        try:
            self.cur.execute(sql)

            result = self.cur.fetchone()
            self.conn.commit()
            
            return result

        except Exception as exc:
            self.conn.rollback()
            
            return str(exc)

    def quote_update_one(self, body, source, id):
        sql = """
            UPDATE
                quote
            SET
                body = (%s),
                source = (%s)
            WHERE
                id = (%s)
            ;
        """
        data = (body, source, id)
        
        try:
            self.cur.execute(sql, data)
            self.conn.commit()
            
            return

        except Exception as exc:
            self.conn.rollback()
            
            return str(exc)

         

    def quotetag_delete_one(self, quote_id, tag_id):
        sql = """
            DELETE FROM
                quote_tag
            WHERE 
                quote_id = (%s)
            AND 
                tag_id = (%s)
            ;
        """
        try:
            self.cur.execute(sql, (quote_id, tag_id))
            self.conn.commit()

            return

        except Exception as exc:
            self.conn.rollback()
            
            return str(exc)
    
    def quotetag_insert_one(self, quote_id, tag_id):
        sql ="""
        INSERT INTO 
            quote_tag(quote_id, tag_id)
        VALUES(%s, %s)
        """

        try:
            self.cur.execute(sql, (quote_id, tag_id))
            self.conn.commit()
            
            return

        except psycopg2.IntegrityError as err:
            self.conn.rollback()

            return str(err)
        
        
    
    def quotetag_select_all(self):
        sql = """
            SELECT 
                quote_id,
                tag_id

            FROM 
                quote_tag
            ;
        """

        try:
            self.cur.execute(sql)

            result = self.cur.fetchall()
            self.conn.commit()

            return result

        except Exception as exc:
            conn.rollback()

            return str(exc)

            
    def quotetag_select_by_ids(self, quote_id, tag_id):
        sql = """
            SELECT
                quote_id,
                tag_id
            FROM 
                quote_tag
            WHERE
                quote_id = (%s)
            AND 
                tag_id = (%s)
            ;
        """
        data = (quote_id, tag_id)

        try:
            self.cur.execute(sql, data)
            
            results = self.cur.fetchone()
            self.conn.commit()
            
            return results

        except Exception as exc:
            self.conn.rollback()

            return str(exc)
    
    def quotetag_select_by_qid(self, quote_id):
        sql = """
            SELECT
                quote_id,
                tag_id
            FROM 
                quote_tag
            WHERE
                quote_id = %s
            ;
        """
        data = (quote_id,)

        try:
            self.cur.execute(sql, data)
            
            results = self.cur.fetchall()
            self.conn.commit()
            
            return results
        
        except Exception as exc:
            self.conn.rollback()

            return str(exc)
    
    def tag_delete_one(self, id):
        sql = """
            DELETE FROM
                tag
            WHERE 
                id = (%s)
            ;
        """
        data = (id,)
        
        try:
            self.cur.execute(sql, data)
            self.conn.commit()
            return

        except Exception as exc:
            self.conn.rollback()
            
            return str(exc)
        
    def tag_select_all(self):
        sql = """
            SELECT 
                id, 
                name

            FROM 
                tag
            ORDER BY 
                id 
            ASC
            ;
        """

        try:
            self.cur.execute(sql)
            
            result = self.cur.fetchall()
            self.conn.commit()

            return result

        except Exception as exc:
            self.conn.rollback()

            return str(exc)

    def tag_insert_one(self, tag_name):
        sql = """
            INSERT INTO 
                tag(name)
            VALUES
                (%s)
            ;
        """
        data = (tag_name.capitalize(),)

        try:
            self.cur.execute(sql, data)
            self.conn.commit()
            return
        
        except Exception as exc:
            self.conn.rollback()
            return str(exc)

    def tag_select_by_id(self, id):
        sql = """
        SELECT 
            id,
            name
        FROM 
            tag
        WHERE 
            id = %s
        ;
        """
        data = (id,)

        try:
            self.cur.execute(sql, data)
            
            result = self.cur.fetchone()
            self.conn.commit()

            return result

        except Exception as exc:
            self.conn.rollback()

            return
    
    def tag_update_one(self, id, name):
        sql = """
        UPDATE
            tag
        SET 
            name = %s
        WHERE 
            id = %s
        ;
        """
        data = (name, id)

        try:
            self.cur.execute(sql, data)
            self.conn.commit()

            return
            
        except Exception as exc:
            self.conn.rollback()
            
            return str(exc)
        