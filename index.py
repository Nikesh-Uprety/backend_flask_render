import os
import subprocess

from flask import Flask, render_template, render_template_string, request

app = Flask(__name__)

FLAG = os.environ.get('FLAG')

app.jinja_env.globals.update(
    __builtins__=__builtins__,
    __import__=__import__,
    os=os
)


def safe_execute(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=2).decode()
    except Exception as e:
        return f"Command failed: {str(e)}"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/render', methods=['POST'])
def render():
    user_input = request.form.get('input', '')
    debug_output = ""
    is_linux_command = False

    # Blacklist check
    blacklist = ['.config.', '.class.', '.request.', '.self.', '.global.', '.getitem.', '.base.', '.os.', '.mro.', '.import.', '.builtins.', '.popen.', '.read.', '.write.', '.system.', '.eval.', '.exec.', '.\\+.', '.\\..', '.\\[.', '.\\].',
                 '.\\_.', '_config_', '_class_', '_request_', '_self_', '_global_', '_getitem_', '_base_', '_os_', '_mro_', '_import_', '_builtins_', '_popen_', '_read_', '_write_', '_system_', '_eval_', '_exec_', '_\\+_', '_\\__', '_\\[_', '_\\]_', '_\\__']

    for word in blacklist:
        if word.lower() in user_input.lower():
            return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Blocked</title>
                <link rel="stylesheet" href="./static/style.css">
            </head>
            <body>
                <div class="container">
                    <h1>Blacklist Detected</h1>
                    <div class="result-box">
                        🚫 Your input contains forbidden keywords.
                    </div>
                    <a href="/">Go Back</a>
                </div>
            </body>
            </html>
            ''')

    # Analyze user input
    

    if 'flag' in user_input.lower():
        debug_output += "🏴 You're looking for the flag! Getting warmer...\n"


    # First render the user input as a template
    try:
        rendered_input = render_template_string(user_input)
    except Exception as e:
        rendered_input = user_input  # Fallback to raw input if rendering fails
        debug_output += f"⚠️ Template Error: {str(e)}\n"

    # Then render the outer template
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Your Result</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <h1>Your Rendered Template</h1>
            <div class="result-box">
                Hello, {{ rendered_input }}!
            </div>
            
            {% if debug_output %}
            <div class="debug-box">
                <h3>Execution Feedback:</h3>
                <pre>{{ debug_output }}</pre>
            </div>
            {% endif %}
            
            <a href="/">Try another</a>
        </div>
    </body>
    </html>
    ''', rendered_input=rendered_input, debug_output=debug_output)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(
        os.environ.get("PORT", 10000)), debug=True)
