from database import engine
from sqlalchemy import inspect

# Check the current columns in the students table
inspector = inspect(engine)
columns = inspector.get_columns('students')
print('Current columns in students table:')
for col in columns:
    print(f'  - {col["name"]}: {col["type"]}')