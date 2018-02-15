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


@register.filter(name='section_name')
def get_section_name(questions):
    if len(questions) != 0:
        fq = questions[0]
        q_type = fq.get('type')
        section = {
            1: 'Diagnostic Rhyme Test (DRT)',
            2: 'Modified Diagnostic Rhyme Test (MRT)',
            3: 'Mean Opinion Score (MOS)'
        }
        return section.get(q_type)
    else:
        return 'No Questions Found'
