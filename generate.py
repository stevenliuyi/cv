#!/usr/bin/env python3
import os
import yaml
import re
import copy
from jinja2 import Environment, FileSystemLoader

yaml_name = 'cv.yml'
template_name = 'cv-template.tex'
output_name = 'cv.tex'


def date_format(s):
    s = str(s)
    s = re.sub(r'(\d+)', r'\DatestampY{\1}', s)
    s = re.sub('-', '--', s)
    return s


def html2latex(s):
    s = re.sub(r'<a[^>]*href="([^">]*)"[^>]*>([^<]*)</a>', r'\href{\1}{\2}',
               s)  # link
    s = re.sub(r'\s*<i[^>]*iconfont[^>]*>([^<]*</i>\s*)', '',
               s)  # remove icons
    s = re.sub(r'<i>([^<]*)</i>', r'\\textit{\1}', s)  # italic
    s = re.sub(r'<span[^>]*under[^>]*>([^<]*)</span>', r'\underline{\1}',
               s)  # underline
    return s


class RenderContext(object):
    def __init__(self, jinja_options, replacements):
        self._replacements = replacements
        self._jinja_options = jinja_options.copy()
        self._jinja_options['loader'] = FileSystemLoader(
            searchpath=os.getcwd())
        self._jinja_env = Environment(**self._jinja_options)

        # add custom filter methods
        self._jinja_env.filters['date_format'] = date_format
        self._jinja_env.filters['html2latex'] = html2latex

    def make_replacements(self, yaml_data):
        # make a copy of the yaml_data so that this function is idempotent
        yaml_data = copy.copy(yaml_data)

        if isinstance(yaml_data, str):
            for o, r in self._replacements:
                yaml_data = re.sub(o, r, yaml_data)

        elif isinstance(yaml_data, dict):
            for k, v in yaml_data.items():
                yaml_data[k] = self.make_replacements(v)

        elif isinstance(yaml_data, list):
            for idx, item in enumerate(yaml_data):
                yaml_data[idx] = self.make_replacements(item)

        return yaml_data

    def render_template(self, yaml_data):
        return self._jinja_env.get_template(template_name).render(yaml_data)

    def render_resume(self, yaml_data):
        yaml_data = self.make_replacements(yaml_data)
        return self.render_template(yaml_data)

    def write_to_outfile(self, output_data):
        with open(output_name, 'wb') as out:
            output_data = output_data.encode('utf-8')
            out.write(output_data)


LATEX_CONTEXT = RenderContext(
    dict(
        block_start_string='~<',
        block_end_string='>~',
        variable_start_string='<<',
        variable_end_string='>>',
        comment_start_string='<#',
        comment_end_string='#>',
        trim_blocks=True,
        lstrip_blocks=True), [('&', '\&')])


def process_resume(context, yaml_data):
    rendered_resume = context.render_resume(yaml_data)
    context.write_to_outfile(rendered_resume)


def read_yaml():
    yaml_data = {}
    with open(yaml_name) as f:
        yaml_data.update(yaml.load(f))

    return yaml_data


def compile():
    os.system(f'latexmk -xelatex {output_name}')
    #os.system('latexmk -c') # clean up


def main():
    yaml_data = read_yaml()
    process_resume(LATEX_CONTEXT, yaml_data)
    compile()


if __name__ == "__main__":
    main()
