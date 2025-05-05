from setuptools import setup, find_packages

setup(
    name="autoAtendeAI",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'flask-restx',
        'flask-jwt-extended',
        'flask-migrate',
        'python-dotenv',
        'psycopg2-binary',
    ],
) 