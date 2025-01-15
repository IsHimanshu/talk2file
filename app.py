import os
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename
import talk2vectorDb
import upload2vectorDb
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize vectorstore as None at module level
vectorstore = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload_file", methods=["POST"])
def upload_file():
    global vectorstore
    try:
        username = request.form["username"]
        files = request.files.getlist("file")

        if not username:
            return "Username is required", 400

        if not files or not any(file.filename for file in files):
            return "No files uploaded", 400

        directory_name = "../" + username
        session["username"] = username

        # Create directory if doesn't exist
        os.makedirs(directory_name, exist_ok=True)

        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(directory_name, filename)
                file.save(file_path)
                print(f"File {filename} saved in {directory_name}")

        # Initialize vectorstore
        vectorstore = upload2vectorDb.read_file_and_save_to_faiss(directory_name)
        session['has_files'] = True
        print("Vectorstore initialized successfully")

        return redirect(url_for("chat"))
    except Exception as e:
        print(f"Error in upload_file: {str(e)}")
        return f"Error processing upload: {str(e)}", 500

@app.route("/chat")
def chat():
    username = session.get("username", "Guest")
    chat_history = session.get("chat_history", [])
    has_files = session.get('has_files', False)
    
    if not has_files:
        chat_history.append("System: Please upload files first to enable chat functionality.")
        session["chat_history"] = chat_history
    
    return render_template("chat.html", 
                         username=username, 
                         chat_history=chat_history,
                         has_files=has_files)

@app.route("/send_message", methods=["POST"])
def send_message():
    global vectorstore
    
    if vectorstore is None:
        return jsonify({
            "error": "No files loaded",
            "chat_history": ["System: Please upload files first to enable chat functionality."]
        }), 400

    #try:
    message = request.form["message"]
    print(f"Received message: {message}")
    
    chat_history = session.get("chat_history", [])
    chat_history.append(f"You: {message}")
    print("Send message to backend:", message)

    #try:
    server_response = talk2vectorDb.retrieve_answers_from_faiss(
        vectorstore, message
    )
    print("Server response:", server_response)
    #except Exception as e:
    print(f"Error retrieving response: {str(e)}")
    server_response = "Error: Unable to process your request. Please try uploading your files again."
        
    chat_history.append(server_response)
    session["chat_history"] = chat_history
    
    return jsonify({"chat_history": chat_history})

    #except Exception as e:
    print(f"Error in send_message: {str(e)}")
    return jsonify({
        "error": str(e),
        "chat_history": session.get("chat_history", []) + ["System: An error occurred processing your message."]
    }), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)