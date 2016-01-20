# probably better to rewrite this using map so that it can be parallelized
# -1 = did not match any templates
def apply_templates(templates, lines):
    template_ids = list()
    for line in lines:
        matched = False
        for template in templates:
            if template.match.match(line):
                template_ids.append(template.id)
                matched = True
        if not matched:
            template_ids.append(-1)
    return template_ids
