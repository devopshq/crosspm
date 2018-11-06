def get_object_from_string(object_path):
    """
    Return python object from string
    :param object_path: e.g os.path.join
    :return: python object
    """
    # split like crosspm.template.GUS => crosspm.template, GUS
    try:
        module_name, object_name = object_path.rsplit('.', maxsplit=1)
        module_ = __import__(module_name, globals(), locals(), ['App'], 0)
        variable_ = getattr(module_, object_name)
    except Exception:
        variable_ = None
    return variable_
