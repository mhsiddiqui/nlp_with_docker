from django.template.defaulttags import register


@register.filter(name='dict_value')
def dict_value(dic, key):
    return dic.get(key)
