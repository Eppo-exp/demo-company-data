# demo_company_data


### schema changes:
1. add holdouts
2. specify what tables each fact should live in (probably need to rethink model structure: poisson for event occurance, binomial/normal/exponential for event value(s))
3. assignment table name (so that we can run multiple use cases in parallel)

### future work:
1. multiple entities
2. event stream data? (i.e., fact dimensions)