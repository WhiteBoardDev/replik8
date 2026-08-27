import jinja2
import jinja2

env = jinja2.Environment(
    loader=jinja2.PackageLoader("templates", '.'),
    
    auto_reload=True
)


def render(template_name: str, template_args: any):
    template = env.get_template(template_name)
    return template.render(template_args).encode('utf-8')