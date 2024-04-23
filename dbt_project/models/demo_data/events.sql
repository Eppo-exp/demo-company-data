select anonymous_user_id
    ,  dateadd('ns', DATE, '1970-01-01') AS event_timestamp
    ,  'checkout'   as event_name
    ,  1 as each_value
  from customer_db.demo_dev.checkout

  union all

  select anonymous_user_id
    ,  dateadd('ns', DATE, '1970-01-01') AS event_timestamp
    ,  'add_to_cart'   as event_name
    ,  1 as each_value
  from customer_db.demo_dev.add_to_cart

  union all

  select anonymous_user_id
    ,  dateadd('ns', DATE, '1970-01-01') AS event_timestamp
    ,  'search'   as event_name
    ,  1 as each_value
  from customer_db.demo_dev.searches
