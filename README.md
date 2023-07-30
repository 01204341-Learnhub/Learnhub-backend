# Learnhub Backend

## Getting Started

To get started, follow these steps:

1. **Install Poetry**: If you don't have Poetry installed on your system, you can install it by following the instructions at https://python-poetry.org/docs/#installation.

2. **Install Dependencies**: Once you have Poetry installed, run the following command `poetry install` in the project directory to install all the project dependencies:.


This will create a virtual environment for the project and install all the necessary dependencies inside it.

3. **Activate Virtual Environment**: To work within the project's virtual environment, you can use the following command `poetry shell`.


Activating the virtual environment will ensure that you have access to the project's dependencies without any conflicts with other Python projects or the system Python.

## Running the FastAPI Server

I've created a handy Poetry script to run the FastAPI server quickly. To start the development server, simply use the following command `poetry run dev`.


This will launch the FastAPI server .

## **Running Tests**
 I've already created some simple tests to check the functionality of the backend. You can run these tests using the following command `poetry run pytest`.
