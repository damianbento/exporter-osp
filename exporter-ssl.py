from flask import Flask, jsonify
from flask_basicauth import BasicAuth
import psutil
import subprocess
import json

app = Flask(__name__)
basic_auth = BasicAuth(app)

# Configuración de usuarios y contraseñas
app.config['BASIC_AUTH_USERNAME'] = 'damian'
app.config['BASIC_AUTH_PASSWORD'] = 'damian123'

# Configuración de certificado y clave privada para HTTPS
CERT_FILE = './rdo1.crt'
KEY_FILE = './rdo1.key'

context = (CERT_FILE, KEY_FILE)

@app.route('/mem')
@basic_auth.required
def mem():
    memory = psutil.virtual_memory()
    return jsonify({'usage': memory.percent})

@app.route('/cpu')
@basic_auth.required
def cpu():
    cpu_usage = psutil.cpu_percent()
    return jsonify({'usage': cpu_usage})

@app.route('/disk')
@basic_auth.required
def disk():
    disk_usage = psutil.disk_usage('/')
    return jsonify({'usage': disk_usage.percent})

@app.route('/status')
@basic_auth.required
def status():
    memory = psutil.virtual_memory()
    cpu_usage = psutil.cpu_percent()
    disk_usage = psutil.disk_usage('/')

    return jsonify({
        'memory_usage': memory.percent,
        'cpu_usage': cpu_usage,
        'disk_usage': disk_usage.percent
    })

@app.route('/podman')
@basic_auth.required
def podman_info():
    try:
        # trae el resultado del  'podman ps' para obtener información sobre los contenedores en ejecución
        result = subprocess.run(['podman', 'ps', '--format', 'json'], capture_output=True, check=True, text=True)
        containers = json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Error al obtener información de Podman: {str(e)}'})

    return jsonify({'containers': containers})

@app.route('/nfs')
@basic_auth.required
def nfs_info():
    try:
        # trae el resultado del 'df' 
        result = subprocess.run(['df'], capture_output=True, check=True, text=True)
        df_output = result.stdout
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Error al obtener información de df: {str(e)}'})

    return jsonify({'df_output': df_output})

@app.route('/vms')
@basic_auth.required
def get_vm_info():
    try:
        # Obtener la lista de nombres de todas las máquinas virtuales
        vm_names = subprocess.check_output(['virsh', 'list', '--all', '--name']).decode('utf-8').splitlines()

        vm_info_list = []

        # Iterar sobre cada nombre de máquina virtual y obtener el nombre con virsh dumpxml
        for vm_name in vm_names:
            if vm_name.strip():  # Verificar que el nombre no esté vacío o solo contenga espacios
                nova_name = subprocess.check_output(['virsh', 'dumpxml', vm_name]).decode('utf-8')
                nova_name = nova_name.split('<nova:name>')[1].split('</nova:name>')[0]
                vm_info_list.append({'vm_name': vm_name, 'nova_name': nova_name})

        return jsonify({'vms': vm_info_list})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    # Ejecutar la aplicación en modo debug con soporte HTTPS
    app.run(host='0.0.0.0', port=3000, debug=True, ssl_context=context)
