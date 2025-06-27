from flask import Flask, render_template, redirect, request, session, jsonify, url_for, send_from_directory
from concurrent.futures import ThreadPoolExecutor
from werkzeug.utils import secure_filename
from auto_captioner import AutoCaptioner
import uuid
import os

app = Flask(__name__)
app.secret_key = 'gu984uf48zt234ut90z29t9032ut982t0923ut9823zt9u2398t98'
app.config['UPLOAD_VIDEOS_FOLDER'] = 'upload/videos/'

executor = ThreadPoolExecutor(max_workers=4)
futures = {}

@app.before_request
def ensure_user():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session.permanent = True

@app.route('/', methods=['GET', 'POST'])
def index():
    user_id = session['user_id']
    if request.method == 'POST':
        video = request.files.get('video')
        model = request.form.get('model')
        if video:
            filename = secure_filename(video.filename)
            _, ext = os.path.splitext(filename)
            os.makedirs(app.config['UPLOAD_VIDEOS_FOLDER'], exist_ok=True)
            save_name = f"{user_id}{ext}"
            save_path = os.path.join(app.config['UPLOAD_VIDEOS_FOLDER'], save_name)
            video.save(save_path)
            session['video_filename'] = save_name
            future = executor.submit(AutoCaptioner(save_path, model).run)
            futures[user_id] = future
            return redirect(url_for('processing'))
    return render_template('index.html')

@app.route('/processing')
def processing():
    return render_template('index.html', is_processing=True)

@app.route('/api/completed', methods=['POST'])
def completed():
    user_id = session.get('user_id')
    future = futures.get(user_id)
    if not future:
        return jsonify({'error': 'no job found'}), 404
    if future.done():
        futures.pop(user_id, None)
        return jsonify({'completed': True})
    return jsonify({'completed': False})

@app.route('/result')
def result():
    orig = session.get('video_filename')
    name, ext = os.path.splitext(orig)
    output_name = f"{name}_output{ext}"
    return render_template('result.html', filename=output_name)

@app.route('/video/<filename>')
def video(filename):
    return send_from_directory(app.config['UPLOAD_VIDEOS_FOLDER'], filename, as_attachment=False)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_VIDEOS_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)
