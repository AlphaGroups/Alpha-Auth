# app/templates/__init__.py

# from jinja2 import Environment, FileSystemLoader
# import os

# TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "email")
# env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

# def render_template(template_name: str, **kwargs) -> str:
#     template = env.get_template(template_name)
#     return template.render(**kwargs)


from jinja2 import Environment, FileSystemLoader
import os

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "email")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def render_template(template_name: str, **kwargs) -> str:
    template = env.get_template(template_name)
    return template.render(**kwargs)
