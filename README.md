# GranaBox - Backend

This is the backend of the **GranaBox** application, developed as part of the **Software Engineering** course at **PUC Rio**. The GranaBox backend is responsible for managing and processing data related to personal finance management, including income and expenses, using a RESTful API.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Overview

GranaBox is a personal finance management tool that helps users:
- Organize and categorize income and expenses.
- Manage recurring and one-time transactions.
- Track their financial status via a RESTful API.
  
This backend is built to handle the logic and database operations behind the frontend's user interface. The backend communicates with the frontend through API requests and processes financial data to provide insights for users.

## Features

- **RESTful API**: Built with Flask, it enables users to interact with their financial data through HTTP requests.
- **CRUD Operations**: Create, Read, Update, and Delete operations for transactions and categories.
- **Swagger Documentation**: Easily accessible API documentation.
- **SQLite Integration**: Uses SQLite as the database to store and manage transaction data.
- **Error Handling**: Includes error responses for invalid or failed operations.
  
## Technologies

The following technologies are used in the development of this backend:

- **Flask**: A lightweight WSGI web application framework in Python.
- **Flask-SQLAlchemy**: An ORM (Object Relational Mapper) for managing the SQLite database.
- **Flask-Swagger**: For automatically generating API documentation.
- **SQLite**: Database to store transaction records.
- **Python 3.x**: The main programming language used in the project.
  
## Installation

### Prerequisites

Before running the project, ensure you have the following installed:
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- A modern web browser (Chrome, Firefox, etc.)

**Important:** Before running the backend or (frontend + backend), you must create a `.env` file in the backend root directory with your Auth0 credentials.

This file is **not included in the repository** for security reasons.

Create a `.env` file containing:

```env
AUTH0_DOMAIN=your-auth0-domain.auth0.com
AUTH0_CLIENT_ID=your-auth0-client-id
AUTH0_AUDIENCE=your-auth0-api-audience
```

> **Note:** The frontend does **not** require its own `.env` file with Auth0 credentials.

### Option 1: Run as part of the full application (with frontend)

This project is typically executed as part of the full GranaBox application using Docker Compose from the frontend repository.

1. **Clone the repository**:

   ```bash
   git clone https://github.com/thiagosnuness/granabox_frontend.git
   git clone https://github.com/thiagosnuness/granabox_backend.git
   ```

2. **Navigate to the project folder** (which contains the `docker-compose.yml` file):

   ```bash
   cd granabox_frontend
   ```

3. **Run the entire application (frontend + backend)** using Docker Compose:
   
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:

   Open your browser and go to [http://localhost](http://localhost)

   You will be redirected to the login page (via Auth0) and, after authentication, the dashboard will load.

   You can explore all available backend endpoints via Swagger UI: [http://localhost:5000/openapi/](http://localhost:5000/openapi/)

### Option 2: Run the backend API standalone with Docker

You can also run the backend independently using Docker:

1. **Clone the backend repository**:

   ```bash
   git clone https://github.com/thiagosnuness/granabox_backend.git
   cd granabox_backend
   ```

2. **Build the Docker image**:

   ```bash
   docker build -t granabox-backend .
   ```

3. **Run the container**:

   ```bash
   docker run -d -p 5000:5000 --name granabox-backend granabox-backend
   ```

4. **Access the backend API documentation**:

   Visit [http://localhost:5000/openapi/](http://localhost:5000/openapi/)

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the **MIT License**. See the [LICENSE](./LICENSE) file for more details.

## Contact

For any questions, feedback, or suggestions, feel free to reach out:

- **Thiago Nunes** - [GitHub Profile](https://github.com/thiagosnuness)
- **Project Backend Repository**: [GranaBox Backend](https://github.com/thiagosnuness/granabox_backend)
- **Project Frontend Repository**: [GranaBox Frontend](https://github.com/thiagosnuness/granabox_frontend)
