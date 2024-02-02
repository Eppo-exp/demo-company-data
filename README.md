# demo_company_data

## Setting local environment:
Create a file `local/profile.yml`:

```
account: ...
user: ...
password: ...
role: ...
database: dbt_analytics
warehouse: EPPO_TEST
schema: ...
```


## Future work:
1. connecting multiple entities (i.e., driver, ride, passenger)
2. event stream data? (i.e., fact dimensions)
3. holdouts
4. assignment table name
5. post to Eppo API to automatically create experiments
6. delete experiments / keep app clean
7. preview environment?
8. create test and production environments, CI/CD, etc.

### API changes that could be nice
1. delete flags via API
2. connect feature flag to experiment
