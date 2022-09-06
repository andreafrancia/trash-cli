def older_than(days_ago, now_value, deletion_date):
    from datetime import timedelta
    limit_date = now_value - timedelta(days=days_ago)
    return deletion_date < limit_date
