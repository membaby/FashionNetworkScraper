import mysql.connector

class Pipeline:
    HOST = 'localhost'
    USER = 'root'
    PORT = 3306
    PASSWORD = 'brands123'

    def __init__(self):
        db = mysql.connector.connect(
            host = self.HOST,
            user = self.USER,
            port = self.PORT,
            password = self.PASSWORD,
        )
        cursor = db.cursor()
        cursor.execute('DROP DATABASE IF EXISTS fashion_network')
        cursor.execute('CREATE DATABASE IF NOT EXISTS fashion_network')
        cursor.execute('USE fashion_network')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                title        TEXT,
                published_at TEXT,
                author       TEXT,
                reading_time TEXT,
                sub_title    TEXT,
                content      TEXT,
                image        TEXT,
                url          VARCHAR(255) UNIQUE,
                keyword      TEXT,
                section      TEXT,
                created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        db.commit()
        cursor.close()
        db.close()
    
    def DBInstance(self):
        db = mysql.connector.connect(
            host = self.HOST,
            user = self.USER,
            port = self.PORT,
            password = self.PASSWORD,
            database = 'fashion_network'
        )
        return db
    
    def get_articles(self, keyword):
        db = self.DBInstance()
        cursor = db.cursor()
        cursor.execute("SELECT url FROM articles WHERE keyword = %s", (keyword,))
        articles = cursor.fetchall()
        cursor.close()
        db.close()
        return [x[0] for x in articles]
    
    def article_exists(self, url):
        db = self.DBInstance()
        cursor = db.cursor()
        cursor.execute("SELECT url FROM articles WHERE url = %s", (url,))
        article = cursor.fetchone()
        cursor.close()
        db.close()
        return article != None
    
    def insert_article(self, article):
        db = self.DBInstance()
        cursor = db.cursor()
        try:
            cursor.execute('''
                INSERT INTO articles (title, published_at, author, reading_time, sub_title, content, image, url, keyword, section)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                article['Article Title'],
                article['Date of Article'],
                article['author'],
                article['reading_time'],
                article['sub_title'],
                article['Article Details'],
                article['Article Image URL'],
                article['Article URL'],
                article['Keyword'],
                article['section']
            ))
            db.commit()
            cursor.close()
            db.close()
            print(f'[+] ({article["Keyword"]}) Inserted: {article["Article Title"]}')
        except Exception as err:
            print(err)

    def get_articles(self):
        db = self.DBInstance()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM articles')
        articles = cursor.fetchall()
        cursor.close()
        db.close()
        return articles