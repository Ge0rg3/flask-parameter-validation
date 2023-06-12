import flask
from flask import Blueprint, current_app

from flask_parameter_validation import ValidateParameters

docs_blueprint = Blueprint("docs", __name__, url_prefix="/docs", template_folder="./templates")

@docs_blueprint.get("/")
def docs_html():
    config = flask.current_app.config
    docs_arr = []
    for rule in current_app.url_map.iter_rules():
        this_docs = dict()
        methods_str = "["
        for method in rule.methods:
            if method not in ["OPTIONS", "HEAD"]:
                methods_str += method + ", "
        methods_str = methods_str[0:-2] + "] "
        print(methods_str + str(rule))
        rule_func = current_app.view_functions[rule.endpoint]
        fn_list = ValidateParameters().get_fn_list()
        this_docs["rule"] = str(rule)
        this_docs["methods"] = []
        for method in rule.methods:
            this_docs["methods"].append(str(method))
        for fsig, fdocs in fn_list.items():
            if fsig.endswith(rule_func.__name__):
                if fdocs["docstring"] is not None:
                    docstring = fdocs["docstring"]
                    while docstring.startswith("\n"):
                        docstring = docstring[1:]
                    docstring = docstring.replace("\n", "<br/>")
                    this_docs["docstring"] = docstring.replace("    ", "&nbsp;"*4)
                else:
                    this_docs["docstring"] = None
                this_docs["args"] = dict()
                i = 0
                if fdocs["docstring"] is not None:
                    print("'''" + fdocs["docstring"] + "'''")
                for arg in fdocs["argspec"].args:
                    this_arg = dict()
                    this_arg["name"] = arg
                    arg_print = "    " + arg + ": "
                    arg_annots = fdocs["argspec"].annotations[arg]
                    arg_print_type = arg_annots.__name__
                    if hasattr(arg_annots, "__args__"):
                        arg_print_type += "["
                        for annot_arg in arg_annots.__args__:
                            arg_print_type += str(annot_arg.__name__) + ", "
                        arg_print_type = arg_print_type[0:-2] + "]"
                    this_arg["type"] = arg_print_type
                    arg_print += arg_print_type + " in request "
                    arg_loc = fdocs["argspec"].defaults[i]
                    this_arg["loc"] = type(arg_loc).__name__
                    arg_print += type(arg_loc).__name__
                    # print(arg_loc.__dict__)
                    arg_loc_has_params = False
                    this_arg["loc_args"] = dict()
                    for param in arg_loc.__dict__.keys():
                        if arg_loc.__dict__[param] is not None and arg_loc_has_params is False:
                            arg_loc_has_params = True
                            arg_print += " ("
                            if not callable(arg_loc.__dict__[param]):
                                this_arg["loc_args"][param] = arg_loc.__dict__[param]
                            else:
                                this_arg["loc_args"][param] = arg_loc.__dict__[param].__module__+"."+arg_loc.__dict__[param].__name__
                        elif arg_loc.__dict__[param] is not None:
                            arg_print += param + "=" + str(arg_loc.__dict__[param]) + ", "
                            if not callable(arg_loc.__dict__[param]):
                                this_arg["loc_args"][param] = arg_loc.__dict__[param]
                            else:
                                this_arg["loc_args"][param] = arg_loc.__dict__[param].__module__+"."+arg_loc.__dict__[param].__name__
                    if this_arg["loc"] in this_docs["args"]:
                        this_docs["args"][this_arg["loc"]].append(this_arg)
                    else:
                        this_docs["args"][this_arg["loc"]] = [this_arg]
                    if arg_loc_has_params:
                        arg_print = arg_print[0:-2] + ")"
                    print(arg_print)
                    i+=1

        docs_arr.append(this_docs)
    return flask.render_template("fpv_default_docs.html",
                                 site_name=config.get("FPV_DOCS_SITE_NAME", "Site"),
                                 docs=docs_arr,
                                 custom_blocks=config.get("FPV_DOCS_CUSTOM_BLOCKS", []))