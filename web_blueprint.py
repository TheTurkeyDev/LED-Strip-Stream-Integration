from flask import Blueprint, render_template, request, jsonify
import data as data
import display_type

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
