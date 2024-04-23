select anonymous_user_id,
  dateadd('ns', DATE, '1970-01-01') AS assigned_at,
  experiment,
  variant,
  session_referrer,
  user_type
from customer_db.demo_dev.anonymous_user_id_assignments
