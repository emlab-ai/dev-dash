def entity_as_dict(table):
    properties = [p for p in dir(table) if not p.startswith('_') and p not in ('metadata', 'query', 'registry')]
    return {name: getattr(table, name) for name in properties}    