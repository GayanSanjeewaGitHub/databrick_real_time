from setuptools import setup, find_packages

setup(
    name="bank-promo-pipeline",
    version="1.0.0",
    description="Credit Card Promotion Targeting - Hadoop/Spark/Hive Implementation",
    author="Data Engineering Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "pyspark==3.4.1",
        "pandas==2.0.3",
        "psycopg2-binary==2.9.9",
        "python-dotenv==1.0.0",
        "faker==20.1.0",
        "sqlalchemy==2.0.23",
        "pyarrow==14.0.1",
    ],
)
