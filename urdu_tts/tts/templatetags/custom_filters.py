from django.template.defaulttags import register


@register.filter(name='dict_value')
def dict_value(dic, key):
    return dic.get(key)


@register.filter(name='question_help')
def question_help(question_type):
    mdrt_instruction = 'Play sound and select which word was spoken'
    mos_instruction = 'Play sound and rate its quality'

    section_heading_n_instructions = {
        1: mdrt_instruction,
        2: mdrt_instruction,
        3: mos_instruction
    }

    return section_heading_n_instructions.get(question_type)