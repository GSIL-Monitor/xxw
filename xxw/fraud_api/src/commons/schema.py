def validate(schema: dict, data):
    result = {}
    errors = {}
    for key, rule in schema.items():
        if not isinstance(rule, tuple):
            rule = (rule,)
        if not isinstance(rule[0], bool):
            if key not in data:
                errors[key] = f'required'
            convert, *check_list = rule
        else:
            _, convert, *check_list = rule

        value = data.get(key)

        if value is not None:
            try:
                value = convert(value)
                if all(bool(check(value)) for check in check_list):
                    result[key] = value
            except TypeError:
                errors[key] = f'"{value}" is invalid'
            except ValueError:
                errors[key] = f'"{value}" is invalid'

    return result, errors
