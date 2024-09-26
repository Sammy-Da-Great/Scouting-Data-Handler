import config_maker
import create_sql_database
import app_home
## First Script run in the program.
config_maker.initialize_configs()
create_sql_database.create_database()

app_home.start_app()
