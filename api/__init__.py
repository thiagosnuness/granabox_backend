"""
This module initializes the database instance using SQLAlchemy.

It is used to handle all the database-related operations for the application,
including model definitions, queries, and transactions.
"""

from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy instance for database handling
db = SQLAlchemy()
