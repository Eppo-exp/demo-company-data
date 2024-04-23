
select 
    anonymous_user_id as anonymous_id,
    random()  as revenue_id,
    dateadd('ns', DATE, '1970-01-01') AS purchase_timestamp,
    gross_revenue,
    basket_size,
    'organic' as revenue_type
  from customer_db.demo_dev.revenue
