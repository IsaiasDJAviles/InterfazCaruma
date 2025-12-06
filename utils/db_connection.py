"""
Gestión de conexiones a la base de datos
"""

import psycopg2
from psycopg2 import pool
from config.db_config import DB_CONFIG


class Database:
    _connection_pool = None
    
    @classmethod
    def initialize(cls):
        """Inicializa el pool de conexiones"""
        try:
            cls._connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 10, **DB_CONFIG
            )
            print("✓ Pool de conexiones inicializado correctamente")
        except Exception as e:
            print(f"✗ Error al inicializar pool de conexiones: {e}")
            raise
    
    @classmethod
    def get_connection(cls):
        """Obtiene una conexión del pool"""
        if cls._connection_pool is None:
            cls.initialize()
        return cls._connection_pool.getconn()
    
    @classmethod
    def return_connection(cls, connection):
        """Devuelve la conexión al pool"""
        cls._connection_pool.putconn(connection)
    
    @classmethod
    def execute_query(cls, query, params=None):
        """Ejecuta una consulta SELECT"""
        conn = cls.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            print(f"Error en execute_query: {e}")
            raise
        finally:
            cls.return_connection(conn)
    
    @classmethod
    def execute_update(cls, query, params=None):
        """Ejecuta INSERT, UPDATE, DELETE"""
        conn = cls.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error en execute_update: {e}")
            raise
        finally:
            cls.return_connection(conn)
    
    @classmethod
    def execute_insert_returning(cls, query, params=None):
        """Ejecuta INSERT y retorna el ID insertado"""
        conn = cls.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            return result[0] if result else None
        except Exception as e:
            conn.rollback()
            print(f"Error en execute_insert_returning: {e}")
            raise
        finally:
            cls.return_connection(conn)
    
    @classmethod
    def close_all_connections(cls):
        """Cierra todas las conexiones del pool"""
        if cls._connection_pool:
            cls._connection_pool.closeall()
            print("✓ Todas las conexiones cerradas")