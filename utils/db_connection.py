"""
Conexión a la base de datos SQLite
"""
import sqlite3
import os
import sys

class Database:
    _connection = None
    _db_path = None
    
    @staticmethod
    def get_base_path():
        """Obtiene la ruta base de la aplicación"""
        if getattr(sys, 'frozen', False):
            # Si es ejecutable
            return sys._MEIPASS
        else:
            # Si es script Python
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    @staticmethod
    def get_db_path():
        """Obtiene la ruta de la base de datos"""
        if Database._db_path is None:
            base_path = Database.get_base_path()
            Database._db_path = os.path.join(base_path, 'database', 'caruma.db')
            
            # Crear carpeta database si no existe
            db_dir = os.path.dirname(Database._db_path)
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
                print(f"✓ Carpeta creada: {db_dir}")
        
        return Database._db_path
    
    @staticmethod
    def initialize():
        """Inicializa la conexión a la base de datos"""
        try:
            db_path = Database.get_db_path()
            
            # Verificar si la base de datos ya existe
            db_existe = os.path.exists(db_path)
            
            Database._connection = sqlite3.connect(db_path, check_same_thread=False)
            Database._connection.row_factory = sqlite3.Row
            
            # Habilitar claves foráneas
            Database._connection.execute("PRAGMA foreign_keys = ON")
            
            print(f"Conexión a base de datos establecida: {db_path}")
            
            # Si la base de datos es nueva, crear tablas
            if not db_existe:
                print("Base de datos nueva detectada, creando tablas...")
                Database.crear_tablas()
            else:
                print("Base de datos existente encontrada")
            
        except Exception as e:
            raise Exception(f"Error al conectar con la base de datos: {e}")
    
    @staticmethod
    def get_connection():
        """Obtiene la conexión a la base de datos"""
        if Database._connection is None:
            Database.initialize()
        return Database._connection
    
    @staticmethod
    def crear_tablas():
        """Crea las tablas y carga datos iniciales desde schema.sql"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        # Verificar si ya existen tablas
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='categorias'")
        tabla_existe = cursor.fetchone()[0] > 0
        
        if tabla_existe:
            print("✓ Tablas ya existen")
            return
        
        # Buscar archivo schema.sql
        base_path = Database.get_base_path()
        schema_path = os.path.join(base_path, 'database', 'schema.sql')
        
        print(f"📂 Buscando schema en: {schema_path}")
        
        if not os.path.exists(schema_path):
            print(f"✗ ARCHIVO NO ENCONTRADO: {schema_path}")
            raise FileNotFoundError(f"No se encontró schema.sql en: {schema_path}")
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            print(f"✓ Archivo schema.sql encontrado ({len(schema_sql)} caracteres)")
            
            # Ejecutar el script SQL
            cursor.executescript(schema_sql)
            conn.commit()
            
            # Verificar que se crearon las tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tablas = cursor.fetchall()
            print(f"✓ Tablas creadas: {[tabla[0] for tabla in tablas]}")
            
            # Verificar datos de ejemplo en categorías
            cursor.execute("SELECT COUNT(*) FROM categorias")
            count = cursor.fetchone()[0]
            print(f"✓ Categorías insertadas: {count}")
            
            # Verificar datos de ejemplo en insumos
            cursor.execute("SELECT COUNT(*) FROM insumos")
            count = cursor.fetchone()[0]
            print(f"✓ Insumos insertados: {count}")
            
        except Exception as e:
            print(f"✗ Error al cargar schema.sql: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    @staticmethod
    def ejecutar_query(query, params=None):
        """Ejecuta una consulta SELECT y retorna los resultados"""
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al ejecutar query: {e}")
            print(f"Query: {query}")
            if params:
                print(f"Params: {params}")
            raise
    
    @staticmethod
    def ejecutar_comando(query, params=None):
        """Ejecuta un comando INSERT, UPDATE o DELETE"""
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            print(f"Error al ejecutar comando: {e}")
            print(f"Query: {query}")
            if params:
                print(f"Params: {params}")
            raise
    
    @staticmethod
    def close_all_connections():
        """Cierra la conexión a la base de datos"""
        if Database._connection:
            Database._connection.close()
            Database._connection = None
            print("Conexión cerrada")