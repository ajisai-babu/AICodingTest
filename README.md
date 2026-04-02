# Flask Demo

A simple Flask web application with SQLite database and RESTful API.

## Features

- SQLite database with users and posts tables
- RESTful API with JSON responses
- Server-side rendering with Jinja2 templates
- CRUD operations for users and posts

## API Endpoints

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | List all users |
| POST | `/api/users` | Create a user |
| GET | `/api/users/<id>` | Get user by ID |
| PUT | `/api/users/<id>` | Update user |
| DELETE | `/api/users/<id>` | Delete user |

### Posts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/posts` | List all posts |
| POST | `/api/posts` | Create a post |

### Pages

| Endpoint | Description |
|----------|-------------|
| `/` | Home page with blog posts |
| `/users` | User list |
| `/users/<id>` | User detail |
| `/about` | About page |

## Run

```bash
pip install -r requirements.txt
python app.py
```

Visit http://localhost:8000
