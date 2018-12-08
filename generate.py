#!/usr/bin/env python3
import os
import yaml
import re
import copy
import argparse
from jinja2 import Environment, FileSystemLoader


def date_format(s):
    s = str(s)
    s = re.sub(r'(\d+)', r'\DatestampY{\1}', s)
    s = re.sub('-', '--', s)
    return s


def html2latex(s, prefix='', suffix=''):
    s = re.sub(r'<a[^>]*href="([^">]*)"[^>]*>([^<]*)</a>',
               fr'{prefix}\href{{\1}}{{\2}}{suffix}', s)  # link
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


def compile(tex='latexmk'):
    if tex == 'latexmk':
        os.system(f'latexmk -xelatex {output_name}')
    elif tex == 'tectonic':
        os.system(f'tectonic {output_name}')
    #os.system('latexmk -c') # clean up


def main():
    global yaml_name, output_name, template_name

    # parse the arguments
    parser = argparse.ArgumentParser(
        description='Generate LaTex PDF resume from YAML file.')
    parser.add_argument(
        '--tectonic', action='store_true', help='use Tectonic to generate PDF')
    parser.add_argument(
        '-c',
        '--color',
        nargs='?',
        default='000000',
        help='hex color code (e.g. 0d8aba) for the secondary text color')
    parser.add_argument(
        '-y', '--yaml', nargs='?', default='cv.yml', help='input YAML file')
    parser.add_argument(
        '-o',
        '--output',
        nargs='?',
        default='output.tex',
        help='output TeX file')
    parser.add_argument(
        '-t',
        '--template',
        nargs='?',
        default='cv-template.tex',
        help='LaTeX template file')
    args = parser.parse_args()

    # check if color is valid
    color_match = re.search(r'^[0-9a-fA-F]{6}$', args.color)
    if not color_match:
        print(
            'hex color code is not valid. It must contains and only contains 6 hex symbols (0-9 and A-F).'
        )
        exit()

    if not os.path.isfile(args.yaml):
        print(f'{args.yaml} does not exist!')
        exit()

    if not os.path.isfile(args.template):
        print(f'{args.template} does not exist!')
        exit()

    yaml_name = args.yaml
    output_name = args.output
    template_name = args.template

    yaml_data = read_yaml()
    yaml_data['color'] = args.color
    process_resume(LATEX_CONTEXT, yaml_data)

    if args.tectonic:
        compile(tex='tectonic')
    else:
        compile()


if __name__ == "__main__":
    main()
