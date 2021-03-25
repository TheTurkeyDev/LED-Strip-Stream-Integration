from flask import Blueprint, render_template, request, jsonify
import data as data
import display_type
import re

api = Blueprint('api', __name__)


@api.route("/")
def hello():
    display_type_map = [{'name': e.name, 'value': e.value} for e in display_type.DisplayType]
    return render_template('index.html', settings={'colors': data.colors, 'brightness': data.brightness,
                                                   'display_types': display_type_map})


@api.route("/setledbrightness", methods=['POST'])
def set_led_color():
    data.brightness = request.args.get('brightness')
    return jsonify(success=True, message="Brightness set!")


@api.route("/setdisplay", methods=['POST'])
def set_display_type():
    data.display = display_type.DisplayType(int(request.args.get('display')))
    return jsonify(success=True, message="Display set!")


@api.route("/addcolor", methods=['POST'])
def add_color():
    color = request.args.get('color')
    if re.match(r"[a-f0-9]{6}", color):
        tuple_color = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        data.colors.append(tuple_color)
        return jsonify(success=True, message="Color Added!", color=tuple_color, index=len(data.colors) - 1)
    return jsonify(success=False, message="Error!")


@api.route("/removecolor", methods=['POST'])
def remove_color():
    data.colors.pop(int(request.args.get('index')))
    return jsonify(success=True, message="Color Removed!")
