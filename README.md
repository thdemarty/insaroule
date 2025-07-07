# INSA'Roule
This repository contains all the code for the INSA'Roule project.

## Getting started
### Development environment
Follow the following steps to set up a development environment:
1. Create a virtual environment and activate it:
    
    ```bash
    python3 -m venv env
    source env/bin/activate
    ```
2. Now that we are in our virtual environment, we need to install the dependencies for the project and for the developement. To do so, we will use `uv` by running the following command:
    
    ```bash
    pip install uv
    ```
    > `uv` is a package manager that allows us to install dependencies way faster than the usual `pip` command.

3. To install the dependencies, we can run the following command:
    
    ```bash
    uv pip install -r requirements.txt
    uv pip install -r requirements-dev.txt
    ```

4. Copy the `.env.dist` to `.env` and fill in the values.

5. Install pre-commit hooks by running the following command:
    
    ```bash
    pre-commit install
    ```

    > This will ensure that the code is formatted correctly and that the tests pass before committing.


6. To run the server, you can use the following command (migrate runs the database migrations and compilemessages compiles the translations to be usable directly in the web application):
    
    ```bash
    cd project
    python manage.py migrate
    python manage.py compilemessages
    python manage.py runserver
    ```

    > [!NOTE] 
    > If you ever run into issues with the database, since this code is currently in development, it is highly recommended to reset the database by deleting the `db.sqlite3` file and running the migrations again:
    > ```bash
    > rm db.sqlite3
    > python manage.py migrate
    > ```
    > 