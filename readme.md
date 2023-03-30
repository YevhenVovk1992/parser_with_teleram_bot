# Parser and bot

### How to start project?
1. Create a virtual environment and run `pip install -r requirements.txt`;
2. Create .env file and write to it enviroment variables:
	- POSTGRES_USER
	- POSTGRES_PASSWORD
	- DB_PORT
	- POSTGRES_DB
	- DB_HOST
    - BOT_TOKEN
3. Run `docker-compose up -d` to make a container with Postgres DB;
4. Create database with the name like in .env file;
5. Create table "article" in database.
`CREATE TABLE article (
	article_id serial PRIMARY KEY,
	title VARCHAR ( 500 ) UNIQUE NOT NULL,
	link TEXT UNIQUE NOT NULL,
	created_at timestamp default now()
);`
6. Run `python3 parser.py`. Please wait while the parser collects information into the database. 
When 'Check a new article...' was written in the console - stop parser.
7. Run `python3 bot.py`. And run command `python3 parser.py` in other console. 
