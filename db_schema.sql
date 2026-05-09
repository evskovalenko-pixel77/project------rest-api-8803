CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  email TEXT UNIQUE,
  password_hash TEXT,
  api_token TEXT
);
CREATE TABLE tasks (
  id INTEGER PRIMARY KEY,
  title TEXT,
  description TEXT,
  completed BOOLEAN DEFAULT 0,
  user_id INTEGER REFERENCES users(id)
);