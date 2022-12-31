from flask import Flask, render_template
import os

app = Flask(__name__)
app.config['IMAGE_FOLDER'] = os.path.join('static', 'images')

@app.route('/')
def index():
#    return 'Hello world'
    full_filename = os.path.join(app.config['IMAGE_FOLDER'], 'image.jpg')
    return render_template('timelapse.html', image=full_filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
