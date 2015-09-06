from sqlalchemy import desc

def generate_query(query, model_cls,
                   where=None, order_by=None, limit=None, offset=None, start=None, end=None):
    if where:
        query = add_where(query, model_cls, where)
    if order_by:
        query = add_order_by(query, model_cls, order_by)
    if limit:
        query = query.limit(int(limit))
    if offset:
        query = query.offset(int(offset))
    if start or end:
        # apply LIMIT/OFFSET to the ``Query`` based on a range
        query = add_start_end(query, start, end)

    return query


def add_where(query, model_cls, where):
    if where:
        query = query.where(where)

    return query


def add_order_by(query, model_cls, order_by):
    cols = []
    if type(order_by) is str or type(order_by) is unicode:
        if ',' in order_by:
            cols = order_by.split(',')
        else:
            cols.append(order_by)
    else:
        cols = order_by
    for order_by in cols:
        if order_by.lower().endswith(' desc'):
            query = query.order_by(desc(getattr(model_cls, order_by.strip().split(' ')[0])))
        elif order_by.lower().endswith(' asc'):
            query = query.order_by(getattr(model_cls, order_by.strip().split(' ')[0]))
        else:
            query = query.order_by(getattr(model_cls, order_by))

    return query


def add_start_end(query, start, end):
    if start:
        start = int(start)
    if end:
        end = int(end)
    if start or end:
        # apply LIMIT/OFFSET to the ``Query`` based on a range
        query = query.slice(start, end)

    return query
