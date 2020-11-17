from flask import Blueprint, render_template, request, jsonify
import data as data

api = Blueprint('api', __name__)


@api.route("/")
def hello():
    return render_template('index.html', settings={'color': '#%02x%02x%02x' % (data.red, data.green, data.blue)})


@api.route("/setledcolor", methods=['POST'])
def set_led_color():
    color = request.args.get('color')
    rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
    data.colors = [rgb]
    return jsonify(success=True, message="Color set!")
