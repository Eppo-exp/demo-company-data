# demo_company_data

## About

This project provides functionality for generating experimentation dummy data for a variety of common use cases. Examples include general user level randomization and metrics, experiments that are randomized on an anonymous ID but measured using user ID-level metrics, and clustered experiments (e.g., experiments randomized by company, but measured using user-level metrics).

Specific use cases are defined in yaml. You can find several examples in the `use-cases` directory.


## Setup

Currently, the project supports writing data to a Snowflake account. If you'd like to use a different warehouse, you'll simply need to reimplement the `push_data` method in `src/snowflake_connector.py`.

### Preparing local environment local

Create a file `local/profile.yml`:

```
account: ...
user: ...
password: ...
role: ...
database: ...
warehouse: ...
schema: ...
```

Next, install dependencies:

```
pip install -r requirements.txt
```

### Simulate data and push to snowflake

Run `main.py` and pass in the use case file you'd like to use:

```
python main.py use-cases/anonymous_users.yml
```

You should now see data in the Snowflake warehouse specified in `local/profile.yml`!