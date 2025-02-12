from flask import Flask, request, jsonify
import subprocess
import os
import json

app = Flask(__name__)

with open('configapps.json', 'r') as config_file:
    apps = json.load(config_file)

print("Loaded app configurations:")
for app_name, app_config in apps.items():
    print(f"- {app_name}: repo_path={app_config['repo_path']}, container_name={app_config['container_name']}")

@app.route('/webhook/<app_name>', methods=['POST'])
def webhook(app_name):
    if app_name not in apps:
        return jsonify({"error": "App not found"}), 404

    repo_path = apps[app_name]["repo_path"]
    container_name = apps[app_name]["container_name"]

    try:
        os.chdir(repo_path)
        
        subprocess.run(["git", "pull"], check=True)
        subprocess.run(["docker", "build", "-t", container_name, "."], check=True)
        subprocess.run(["docker", "stop", container_name], check=False)
        subprocess.run(["docker", "rm", container_name], check=False)
        subprocess.run(["docker", "run", "-d", "--name", container_name, container_name], check=True)
        
        return jsonify({"message": f"{app_name} updated and restarted successfully"})
    
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Failed during process: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
