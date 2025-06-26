from flask import Flask, render_template, Response, jsonify, send_file
import subprocess
import os
import html

app = Flask(__name__)
BUILD_DIR = "/root/esp/hello_world"
EXPORT_SCRIPT = os.path.expanduser("~/esp/esp-idf/export.sh")
ELF_PATH = os.path.join(BUILD_DIR, "build", "hello_world.elf")


def is_idf_initialized():
    return "IDF_PATH" in os.environ


def highlight_log_line(line):
    line = html.escape(line)
    if "error" in line.lower():
        return f'<span style="color:red;">{line}</span>'
    elif "warning" in line.lower():
        return f'<span style="color:orange;">{line}</span>'
    elif "success" in line.lower() or "done" in line.lower():
        return f'<span style="color:green;">{line}</span>'
    elif "build complete" in line.lower():
        return f'<span style="color:cyan;">{line}</span>'
    return line


def run_build():
    env = os.environ.copy()
    if not is_idf_initialized():
        export_cmd = f"bash -c 'source {EXPORT_SCRIPT} && env'"
        result = subprocess.run(export_cmd, shell=True, capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                env[key] = value

    build_cmd = f"bash -c 'cd {BUILD_DIR} && idf.py build'"
    process = subprocess.Popen(build_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)

    for line in process.stdout:
        colored = highlight_log_line(line.rstrip())
        yield f"data: {colored}\n\n"

    # 检查是否生成 elf
    if os.path.exists(ELF_PATH):
        yield f"data: <span style='color:cyan;'>✅ 构建完成，已生成 ELF 文件。</span>\n\n"
    else:
        yield f"data: <span style='color:red;'>❌ 构建失败，未生成 ELF 文件。</span>\n\n"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/build")
def build():
    return Response(run_build(), mimetype='text/event-stream')


@app.route("/status")
def status():
    return jsonify({
        "exported": is_idf_initialized(),
        "elf_exists": os.path.exists(ELF_PATH)
    })


@app.route("/elf-info")
def elf_info():
    if not os.path.exists(ELF_PATH):
        return jsonify({"exists": False})

    size = os.path.getsize(ELF_PATH)
    try:
        result = subprocess.run(
            ["xtensa-esp32-elf-size", ELF_PATH],
            capture_output=True, text=True
        )
        chip = "esp32 (示例)" if "text" in result.stdout else "未知"
    except Exception:
        chip = "未知"

    return jsonify({
        "exists": True,
        "size": size,
        "chip": chip
    })


@app.route("/download-elf")
def download_elf():
    if os.path.exists(ELF_PATH):
        return send_file(ELF_PATH, as_attachment=True)
    return "ELF 文件不存在", 404


@app.route("/flash", methods=["POST"])
def flash():
    print("【烧录按钮已经点击】")
    return jsonify({"message": "烧录按钮已经点击"})




if __name__ == "__main__":
        app.run(host='0.0.0.0', debug=True)
