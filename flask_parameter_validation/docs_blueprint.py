import flask
from flask import Blueprint, current_app

from flask_parameter_validation import ValidateParameters

docs_blueprint = Blueprint("docs", __name__, url_prefix="/docs", template_folder="./templates")

def get_docs_arr():
    docs_arr = []
    for rule in current_app.url_map.iter_rules():  # Iterate through all Flask Routes
        this_docs = dict()
        rule_func = current_app.view_functions[rule.endpoint]  # Get the function that the Flask Route calls
        fn_list = ValidateParameters().get_fn_list()  # Get the function list that ValidateParameters accumulates
        this_docs["rule"] = str(rule)  # Get the URL rule for this Route
        # Gather all HTTP methods applicable to this Route
        this_docs["methods"] = []
        for method in rule.methods:
            this_docs["methods"].append(str(method))
        for fsig, fdocs in fn_list.items():  # Iterate through all functions ValidateParameters decorates
            # Find the ValidateParameters function for rule_func - this will find nothing if ValidateParameters isn't
            # the bottommost decorator (confirmation needed), or if ValidateParameters isn't present at all
            if fsig.endswith(rule_func.__name__):
                if fdocs["docstring"] is not None:  # Add docstring to result in HTML format, do not sanitize tags
                    docstring = fdocs["docstring"]
                    while docstring.startswith("\n"):
                        docstring = docstring[1:]
                    docstring = docstring.replace("\n", "<br/>")
                    this_docs["docstring"] = docstring.replace("    ", "&nbsp;" * 4)
                else:
                    this_docs["docstring"] = None
                this_docs["args"] = dict()
                for i in range(len(fdocs["argspec"].args)):  # Iterate through arguments captured by ValidateParameters
                    arg = fdocs["argspec"].args[i]
                    this_arg = dict()  # Store argument data as a dictionary
                    this_arg["name"] = arg  # Argument Name
                    arg_print = "    " + arg + ": "
                    arg_annots = fdocs["argspec"].annotations[arg]  # Argument Type Hint
                    arg_print_type = arg_annots.__name__
                    if hasattr(arg_annots, "__args__"):  # Sub-types of Optional, Union, list, etc.
                        arg_print_type += "["
                        for annot_arg in arg_annots.__args__:
                            arg_print_type += str(annot_arg.__name__) + ", "
                        arg_print_type = arg_print_type[0:-2] + "]"
                    this_arg["type"] = arg_print_type
                    arg_print += arg_print_type + " in request "
                    arg_loc = fdocs["argspec"].defaults[i]
                    this_arg["loc"] = type(
                        arg_loc).__name__  # Where in the Request the Argument comes from, one of FPV's Parameter classes
                    arg_print += type(arg_loc).__name__
                    # print(arg_loc.__dict__)
                    arg_loc_has_params = False
                    this_arg["loc_args"] = dict()
                    for param in arg_loc.__dict__.keys():  # Iterate through arguments to the Parameter constructor
                        if arg_loc.__dict__[param] is not None:
                            if arg_loc_has_params is False:
                                arg_loc_has_params = True
                                arg_print += " ("
                            if not callable(arg_loc.__dict__[param]):  # For non-callable arguments (most arguments)
                                this_arg["loc_args"][param] = arg_loc.__dict__[param]  # Just save it to the dict as is
                            else:  # For callable arguments (func), convert it to the module path and function name
                                this_arg["loc_args"][param] = arg_loc.__dict__[param].__module__ + "." + \
                                                              arg_loc.__dict__[param].__name__
                    if this_arg["loc"] in this_docs[
                        "args"]:  # Does this function aleady have an argument list for this Parameter class?
                        this_docs["args"][this_arg["loc"]].append(this_arg)
                    else:
                        this_docs["args"][this_arg["loc"]] = [this_arg]
                    if arg_loc_has_params:
                        arg_print = arg_print[0:-2] + ")"
                    print(arg_print)
        docs_arr.append(this_docs)
    return docs_arr

@docs_blueprint.get("/")
def docs_html():
    config = flask.current_app.config
    return flask.render_template("fpv_default_docs.html",
                                 site_name=config.get("FPV_DOCS_SITE_NAME", "Site"),
                                 docs=get_docs_arr(),
                                 custom_blocks=config.get("FPV_DOCS_CUSTOM_BLOCKS", []))