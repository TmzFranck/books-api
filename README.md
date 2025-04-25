# Books API

A RESTful API for managing books and their metadata.

## Overview

Books API provides a comprehensive platform for managing a collection of books with the following features:

- **Book Management**: Create, retrieve, update, and delete books
- **User Authentication**: Secure signup, login, and token-based authentication
- **Role-Based Access Control**: Different permissions for users and administrators
- **Review System**: Allow users to post and manage reviews for books
- **Tagging System**: Organize books with custom tags
- **Background Processing**: Email notifications and other async tasks with Celery
- **Token Management**: Secure logout with token blacklisting via Redis

The API is built with FastAPI, providing automatic OpenAPI documentation, async request handling, and modern Python features.

## Getting Started

### Prerequisites

- Python 3.13
- pip for dependency management

### Installation

1. Clone the repository:

   ```
   git clone <repository-url>
   cd books-api
   ```

2. Set up a virtual environment:

   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Configure environment variables:

   ```
   cp .env.example .env
   # Edit .env with your configurations
   ```

5. Run database migrations:

   ```
   # Initialize Alembic if you haven't already
   alembic init migrations

   # Generate a migration
   alembic revision --autogenerate -m "Initial migration"

   # Apply migrations
   alembic upgrade head
   ```

6. Start the development server:

   ```
   # Run the FastAPI application from the src directory
   fastapi dev src/
   ```

7. Start Redis using Docker:

   ```
   docker-compose up -d redis
   ```

8. Start Celery worker for background tasks:

   ```
   celery -A src.celery_tasks.c_app worker --loglevel=INFO
   ```

9. Start Flower for monitoring Celery tasks:
   ```
   celery -A src.celery_tasks.c_app flower
   ```

## API Documentation

### FastAPI Swagger UI

The API documentation is automatically generated and available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Endpoints

#### Books

- `GET /api/books/` - List all books
- `POST /api/books/` - Create a new book
- `GET /api/books/{book_uid}` - Retrieve a specific book
- `PATCH /api/books/{book_uid}` - Partially update a book
- `DELETE /api/books/{book_uid}` - Delete a book
- `GET /api/books/user/{user_uid}` - List books submitted by a specific user

#### Reviews

- `GET /api/reviews/` - List all reviews
- `GET /api/reviews/{review_uid}` - Get a specific review
- `POST /api/reviews/book/{book_uid}` - Add a review for a book
- `DELETE /api/reviews/{review_uid}` - Delete a review

#### Tags

- `GET /api/tags/` - List all tags
- `POST /api/tags/` - Create a new tag
- `POST /api/tags/book/{book_uid}/tags` - Add a tag to a book
- `PUT /api/tags/{tag_uid}` - Update a tag
- `DELETE /api/tags/{tag_uid}` - Delete a tag

#### Authentication

- `POST /api/auth/signup` - Register a new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh_token` - Get a new access token using refresh token
- `POST /api/auth/logout` - Logout (revoke token)
- `GET /api/auth/me` - Get current user information
- `POST /api/auth/send_mail` - Send email notification
- `GET /api/auth/verify/{token}` - Verify user account
- `POST /api/auth/password-reset-request` - Request password reset
- `POST /api/auth/password-reset-confirm/{token}` - Confirm password reset

## Authentication

The API uses token-based authentication with role-based access control. Include the token in the Authorization header:

```
Authorization: Bearer <your-token>
```

### Roles and Permissions

The application implements role-based access control with the following roles:

- **Admin**: Full access to all endpoints and operations
- **User**: Can manage their own books, post reviews, and use tags

Endpoints are protected using role checker dependencies that verify the user has the appropriate permissions for the requested operation.

## Development

### Database Migrations

This project uses Alembic for database migrations:

```
# Create a new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply pending migrations
alembic upgrade head

# Downgrade to a specific version
alembic downgrade <revision>

# View migration history
alembic history
```

### Background Tasks with Celery

This project uses Celery for handling background tasks like sending emails and processing data:

- **Worker**: Processes background tasks from the queue
- **Flower**: Web-based monitoring tool for Celery tasks (available at http://localhost:5555)
- **Redis**: Used as a message broker and for token blacklisting

### Email Testing with MailMung

For development purposes, the application is configured to use MailMung, an online service for email testing that captures and displays emails without actually sending them to real recipients.

To use MailMung:

1. Sign up for a free MailMung account at https://mailmug.net
2. Configure your login information in the `.env` file
3. All emails sent by the application will be viewable in your MailMung dashboard

> Note: MailMung is for development only. Configure a real email service provider for production.

### Redis

Redis serves two primary functions in this project:

1. **Message Broker**: Handles the task queue for Celery workers
2. **Token Blacklisting**: Stores revoked JWT tokens to enforce logout functionality

To access the Redis CLI for debugging:

```
docker exec -it redis redis-cli
```

Useful Redis commands for token management:

```
# List all keys
KEYS *

# Check if a token is blacklisted
EXISTS blacklisted_tokens:<token_jti>

# Set expiration time on keys
TTL blacklisted_tokens:<token_jti>
```

### Testing

This project uses [pytest](https://docs.pytest.org/) for testing, along with FastAPI's TestClient and unittest.mock for mocking dependencies.

To run the test suite:

```
# (Optional) Activate your virtual environment
source .venv/bin/activate

# Install test dependencies if not already installed
pip install -r requirements.txt

# Run all tests
pytest
```

#### Notes

- Tests are located in the `tests/` directory and cover authentication, books, reviews, and tags endpoints.
- Some tests use dependency overrides and mocks for database and Redis interactions.
- Ensure your environment variables are set up (see `.env.example`).
- For best results, run tests in an isolated environment.

### Code Style

This project uses:

- Ruff for linting
- Black for code formatting

Format your code before committing:

```
black .
ruff check --fix
```

## Deployment

Instructions for deploying the API to production environments.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
