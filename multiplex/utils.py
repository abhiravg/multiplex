def to_nested_dict(d, dotlist_sep='.'):
    new = {}

    def add_element(key, value):
        if dotlist_sep in key:
            subdict = new
            for part in key.split(dotlist_sep)[:-1]:
                if part not in subdict:
                    subdict[part] = {}
                subdict = subdict[part]
            subdict[key.split(dotlist_sep)[-1]] = value
        else:
            new[key] = value

    for key, value in d.items():
        add_element(key, value)
    return new
