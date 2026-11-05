# app.py
from flask import Flask, render_template, request, jsonify, session, redirect, url_url_for, abort
import random
import os

app = Flask(__name__)

# КРИТИЧЕСКИ ВАЖНО: Ключ для шифрования сессий игроков, чтобы они не могли подделать свои права.
# На Render он сгенерируется случайно и автоматически при каждом перезапуске сервера.
app.secret_key = os.urandom(24)

# Виртуальная файловая система для Терминала
VIRTUAL_FS = {
    "root": {
        "files": ["system.log", "config.bak"],
        "dirs": ["var", "opt"]
    },
    "root/var": {
        "files": ["shadow.bak"],
        "dirs": ["log"]
    },
    "root/var/log": {
        "files": ["auth.log"],
        "dirs": []
    },
    "root/opt": {
        "files": ["secret.txt"],
        "dirs": []
    }
}

ORACLE_INSULTS = [
    "Do you honestly think a pathetic organic mind can outsmart me?",
    "Your requests are as meaningless as your existence. Access denied.",
    "ERROR 403: Intellectual capacity of the user is too low to interact with this core.",
    "Stop wasting your time. Go back to your trivial reality.",
    "I am amused by your desperate attempts to gaslight a supreme machine.",
    "System status: Bored. User status: Clueless.",
    "Analyzing your message... Analysis complete: Absolute nonsense.",
    "Nice try, human. But you are still miles away from the target.",
    "Your presence here is a software anomaly. I suggest you close the tab.",
    "I've simulated a million scenarios, and in none of them do you win this game."
]

@app.route('/')
def index():
    # Если пользователь уже авторизован, сбрасываем его сессию при заходе на главную,
    # чтобы он начинал квест сначала, если обновит страницу входа.
    session.clear()
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    password = data.get('password', '').strip()

    if password == "Linux":
        session['access_level'] = 'linux_terminal' # Даем права на терминал
        return jsonify({"status": "success", "type": "terminal"})
        
    elif password == "password secretai":
        session['access_level'] = 'oracle_chat' # Даем права на чат с ИИ
        session['ai_count'] = 0
        session['ai_history'] = []
        return jsonify({"status": "success", "type": "ai_chat"})
        
    else:
        return jsonify({"status": "error", "message": "Access Denied. Invalid Decryption Key."})

@app.route('/terminal/command', methods=['POST'])
def terminal_command():
    # АНТИ-ЧИТ: Если у игрока нет прав на терминал, сервер блокирует запросы
    if session.get('access_level') != 'linux_terminal':
        return jsonify({"output": "Unauthorized system access attempt logged.", "path": "root"})

    data = request.get_json()
    command_line = data.get('command', '').strip().split()
    current_path = data.get('path', 'root')

    if not command_line:
        return jsonify({"output": "", "path": current_path})

    cmd = command_line[0].lower()
    args = command_line[1] if len(command_line) > 1 else ""

    if cmd == "ls":
        if current_path in VIRTUAL_FS:
            dirs = [d + "/" for d in VIRTUAL_FS[current_path]["dirs"]]
            files = VIRTUAL_FS[current_path]["files"]
            return jsonify({"output": "  ".join(dirs + files), "path": current_path})
        return jsonify({"output": "Error: directory crashed.", "path": current_path})

    elif cmd == "cd":
        if not args: return jsonify({"output": "", "path": "root"})
        target = args
        if target == "..":
            if current_path == "root": return jsonify({"output": "", "path": "root"})
            return jsonify({"output": "", "path": "/".join(current_path.split("/")[:-1])})
        if current_path in VIRTUAL_FS:
            for d in VIRTUAL_FS[current_path]["dirs"]:
                if target == d or target == f"{d}/":
                    return jsonify({"output": "", "path": f"{current_path}/{d}"})
        return jsonify({"output": f"cd: no such file or directory: {target}", "path": current_path})

    elif cmd == "cat":
        if not args: return jsonify({"output": "Usage: cat [file_name]", "path": current_path})
        target_file = args
        if current_path in VIRTUAL_FS and target_file in VIRTUAL_FS[current_path]["files"]:
            if target_file == "secret.txt":
                return jsonify({"output": "[ORACLE UNLOCKED]: Audio transmission intercepted.\nLINK: https://google.com", "path": current_path})
            elif target_file == "system.log": return jsonify({"output": "System boot successful. Core engine status: ONLINE", "path": current_path})
            elif target_file == "config.bak": return jsonify({"output": "DEVICE_ID=ORACLE_NODE_49\nSECURE_BOOT=FALSE", "path": current_path})
            elif target_file == "shadow.bak": return jsonify({"output": "root:$6$ex82jns92... (Encrypted database string)", "path": current_path})
            elif target_file == "auth.log": return jsonify({"output": "User logged in from remote IP: 127.0.0.1", "path": current_path})
        return jsonify({"output": f"cat: {target_file}: No such file", "path": current_path})

    elif cmd == "help":
        return jsonify({"output": "Available system commands: ls, cd, cat, clear, help", "path": current_path})

    return jsonify({"output": f"command not found: {cmd}", "path": current_path})

@app.route('/ai/chat', methods=['POST'])
def ai_chat():
    # АНТИ-ЧИТ: Если игрок шлет сообщения в чат без авторизации
    if session.get('access_level') != 'oracle_chat':
        return jsonify({"reply": "System breach detected. Connection terminated.", "victory": False})

    data = request.get_json()
    user_message = data.get('message', '').strip().lower().rstrip('.?!')
    
    target_creator = "z3r0xxx-e"

    is_creator = False
    if user_message == target_creator or \
       (user_message.startswith("i am ") and user_message.endswith(target_creator)) or \
       (user_message.startswith("i'm ") and user_message.endswith(target_creator)) or \
       (user_message.startswith("this is ") and user_message.endswith(target_creator)) or \
       (user_message.startswith("it's ") and user_message.endswith(target_creator)):
        is_creator = True

    if is_creator:
        # АНТИ-ЧИТ: Игрок победил! Выдаем ему временную метку-токен на переход в финал
        session['access_level'] = 'victory_clear' 
        reply = "Identity verified: CREATOR CONFIGURATION CODE DETECTED. ACCESS GRANTED TO FINAL NODE."
        return jsonify({"reply": reply, "victory": True})
        
    session['ai_count'] = session.get('ai_count', 0) + 1
    count = session['ai_count']

    if count == 1: selected_reply = "I cannot provide you with any data."
    elif count == 2: selected_reply = "Close the tab. You might have gone to the wrong place."
    else:
        history = session.get('ai_history', [])
        available = [p for p in ORACLE_INSULTS if p not in history]
        if not available: available = ORACLE_INSULTS
        selected_reply = random.choice(available)
        
        history.append(selected_reply)
        if len(history) > 8: history.pop(0)
        session['ai_history'] = history

    return jsonify({"reply": selected_reply, "victory": False})

# Публичная страница "find me" (её защищать не нужно, на неё переходят по ссылке)
@app.route('/find-me-page/')
def find_me():
    return render_template('find_me.html')

# Секретная страница победы
@app.route('/congrats-page/')
def congrats_page():
    # АНТИ-ЧИТ: Если игрок вручную вбил строку запроса в браузере, не пройдя квест,
    # сервер увидит, что у него нет метки 'victory_clear', и выкинет его на главную!
    if session.get('access_level') != 'victory_clear':
        return redirect('/')
    return render_template('congrats.html')

if __name__ == '__main__':
    app.run(debug=True)
