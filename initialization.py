import config_maker
import create_sql_database
import app_home
import os
# First Script run in the program.

if not os.path.isdir("tmp"):
        os.makedirs("tmp")
if not os.path.isdir("tmp/cache"):
        os.makedirs("tmp/cache")

config_maker.initialize_configs()
create_sql_database.create_database()

if __name__ == "__main__":
        app_home.start_app()