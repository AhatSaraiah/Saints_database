# FastAPI Project with Authentication, MySQL, and Amazon S3 Integration

This project is a FastAPI application that provides authentication, MySQL database integration, and Amazon S3 file storage. Users can log in with credentials, and based on their roles, they are redirected to specific routes. User data is stored in a MySQL database, and file uploads are handled by Amazon S3.

## Features

- User authentication with JWT
- MySQL database integration for user management
- Amazon S3 integration for file storage
- Separation of routes for admin, user, and default functionalities
- Custom exception handling

## Prerequisites

Before running the project, ensure that you have the following:

- Python 3.7 or higher installed
- AWS CLI installed and configured with the necessary credentials
- MySQL database connection details configured in `mysql_connection.py`
- Required Python packages installed (`requirements.txt`)

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/your-fastapi-project.git

2. Install dependencies:

     ```bash
     cd your-fastapi-project
     pip install -r requirements.txt
     ```

3. Configure AWS credentials:

4. Make sure to set up your AWS credentials using the AWS CLI or environment variables.

5. Configure MySQL database:

6. Update the connection details in mysql_connection.py with your MySQL database credentials.

7. Run the application:

  ```bash
  uvicorn main:app --reload
  ```

The FastAPI application will be accessible at http://127.0.0.1:8000.

## Usage
1. Log in:

Access the login page at http://127.0.0.1:8000/login and log in with valid credentials. Users are redirected based on their roles.

2. Access role-specific routes:

Admin routes: http://127.0.0.1:8000/admin
User routes: http://127.0.0.1:8000/user
Default routes: http://127.0.0.1:8000/default

3. File uploads:

File uploads are handled through the S3 integration. Implement an endpoint to handle file uploads and associate file paths with users.

## Contributions
Feel free to contribute to this project by opening issues or submitting pull requests. Your feedback and contributions are welcome!

## License
This project is licensed under the MIT License.
