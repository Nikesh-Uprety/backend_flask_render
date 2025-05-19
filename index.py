from flask import Flask, render_template, request, render_template_string
import os
import subprocess

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

    # Analyze user input
    if 'cat' in user_input or 'ls' in user_input or '/' in user_input:
        debug_output += "⚠️ Detected Linux-style command. Remember this server runs on Windows.\n"
        is_linux_command = True

    if '__import__' in user_input or 'os.' in user_input or 'popen' in user_input:
        debug_output += "🔍 Int3resting attempt! You're exploring Python functions.\n"

    if 'flag' in user_input.lower():
        debug_output += "🏴 You're looking for the flag! Getting warmer...\n"

    # Windows-specific hints
    if is_linux_command:
        debug_output += "💡 Windows uses 'type' instead of 'cat', and 'dir' instead of 'ls'\n"
        debug_output += "💡 Try using absolute paths with backslashes (C:\\path\\to\\file)\n"

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
        <link rel="stylesheet" href="/templates/globals.css">
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
    app.run(debug=True)
