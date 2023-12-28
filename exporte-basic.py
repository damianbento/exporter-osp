from flask import Flask, jsonify
import psutil
import subprocess
import json

app = Flask(__name__)

@app.route('/metrics')
def status():
    memory = psutil.virtual_memory()
    cpu_usage = psutil.cpu_percent()
    disk_usage = psutil.disk_usage('/')
    cpu_info = psutil.cpu_times()
    disk_partitions = psutil.disk_partitions()
    network_info = psutil.net_io_counters()
    boot_time = psutil.boot_time()

    # Construir una respuesta en formato Prometheus
    prometheus_response = (
        f'# HELP memory_usage Percentage of memory usage\n'
        f'# TYPE memory_usage gauge\n'
        f'memory_usage {memory.percent}\n'
        f'# HELP cpu_percent CPU usage percentage\n'
        f'# TYPE cpu_percent gauge\n'
        f'cpu_percent {cpu_usage}\n'
        f'# HELP disk_usage Percentage of disk usage\n'
        f'# TYPE disk_usage gauge\n'
        f'disk_usage {disk_usage.percent}\n'
        f'# HELP cpu_info CPU times\n'
        f'# TYPE cpu_info gauge\n'
        f'cpu_info_user {cpu_info.user}\n'
        f'cpu_info_system {cpu_info.system}\n'
        f'cpu_info_idle {cpu_info.idle}\n'
        f'# HELP disk_partitions List of disk partitions\n'
        f'# TYPE disk_partitions gauge\n'
        + '\n'.join([f'disk_partition{{device="{p.device}"}} 1' for p in disk_partitions]) + '\n'
        f'# HELP network_info Network bytes\n'
        f'# TYPE network_info gauge\n'
        f'network_info_bytes_sent {network_info.bytes_sent}\n'
        f'network_info_bytes_recv {network_info.bytes_recv}\n'
        f'# HELP boot_time System boot time\n'
        f'# TYPE boot_time gauge\n'
        f'boot_time {boot_time}\n'
    )

    return prometheus_response

if __name__ == '__main__':
    # Ejecutar la aplicación sin modo de depuración
    app.run(host='0.0.0.0', port=3000)
