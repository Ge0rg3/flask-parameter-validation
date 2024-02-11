import datetime
from pathlib import Path
from typing import Optional
from flask import Blueprint, jsonify, request
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from flask_parameter_validation import ValidateParameters, File

resources = Path(__file__).parent.parent / 'uploads'


def get_file_blueprint(bp_name: str) -> Blueprint:
    file_bp = Blueprint(bp_name, __name__, url_prefix="/file")

    @file_bp.post("/required")
    @ValidateParameters()
    def required(v: FileStorage = File()):
        assert type(v) is FileStorage
        return jsonify({"success": True})

    @file_bp.post("/optional")
    @ValidateParameters()
    def optional(v: Optional[FileStorage] = File()):
        return jsonify({"success": True, "file_provided": v is not None})

    @file_bp.post("/content_types")
    @ValidateParameters()
    def content_types(v: FileStorage = File(content_types=["application/json"])):
        assert v.content_type == "application/json"
        return jsonify({"success": True})

    @file_bp.post("/min_length")
    @ValidateParameters()
    def min_length(v: FileStorage = File(min_length=300)):
        save_path = resources / secure_filename(v.filename)
        v.save(resources / secure_filename(v.filename))
        v.close()
        return jsonify({"success": True, "save_path": str(save_path.absolute())})

    @file_bp.post("/max_length")
    @ValidateParameters()
    def max_length(v: FileStorage = File(max_length=10000)):
        save_path = resources / secure_filename(v.filename)
        v.save(resources / secure_filename(v.filename))
        v.close()
        return jsonify({"success": True, "save_path": str(save_path.absolute())})

    return file_bp