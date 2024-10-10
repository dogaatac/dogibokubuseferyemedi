import argparse
import json
import os
import logging
import randomname
import requests
import subprocess
import time
import psutil
import threading

# Logger ayarları
logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])
logging.basicConfig(
    filename='slave_log.log',
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

COLORS = {
    'HEADER': '\033[95m',
    'OKBLUE': '\033[94m',
    'OKGREEN': '\033[92m',
    'WARNING': '\033[93m',
    'FAIL': '\033[91m',
    'ENDC': '\033[0m',
}

ALGORITHM_NAMES = {
    'c004_a034': 'invector',
    'c003_a032': 'quick_knap',
    'c002_a035': 'cw_heuristic',
    'c001_a034': 'sat_global'
}

def now():
    return int(time.time())

def main(
    master_ip: str,
    tig_worker_path: str,
    download_wasms_folder: str,
    num_workers: int,
    slave_name: str,
    master_port: int,
    total_memory: int,
    gpu_available: bool
):
    logger.info(f"{COLORS['HEADER']}Starting TIG Slave Benchmarker{COLORS['ENDC']}")

    if not os.path.exists(tig_worker_path):
        logger.error(f"tig-worker not found at path: {tig_worker_path}")
        raise FileNotFoundError(f"tig-worker not found at path: {tig_worker_path}")
    os.makedirs(download_wasms_folder, exist_ok=True)

    headers = {
        "User-Agent": slave_name
    }

    algorithm_solutions = {alg: 0 for alg in ALGORITHM_NAMES.values()}

    while True:
        try:
            # Step 1: Query for job
            start = now()
            get_batch_url = f"http://{master_ip}:{master_port}/get-batch"
            resp = requests.get(get_batch_url, headers=headers)
            if resp.status_code != 200:
                logger.error(f"Failed to fetch job: status {resp.status_code}, response: {resp.text}")
                raise Exception(f"status {resp.status_code} when fetching job: {resp.text}")
            batch = resp.json()
            batch_id = f"{batch['benchmark_id']}_{batch['start_nonce']}"
            algorithm_id = batch['settings']['algorithm_id']
            algorithm_name = ALGORITHM_NAMES.get(algorithm_id, "unknown")
            logger.info(f"\n\n{COLORS['OKGREEN']}New batch received: {batch_id[-4:]} for algorithm {COLORS['FAIL']}{algorithm_name}{COLORS['ENDC']}{COLORS['ENDC']}")

            # Step 2: Download WASM
            wasm_path = os.path.join(download_wasms_folder, f"{algorithm_id}.wasm")
            if not os.path.exists(wasm_path):
                resp = requests.get(batch['download_url'])
                if resp.status_code != 200:
                    logger.error(f"Failed to download WASM: status {resp.status_code}, response: {resp.text}")
                    raise Exception(f"status {resp.status_code} when downloading WASM: {resp.text}")
                with open(wasm_path, 'wb') as f:
                    f.write(resp.content)

            # Step 3: Run tig-worker
            start = now()
            cmd = [
                tig_worker_path, "compute_batch",
                json.dumps(batch["settings"]),
                batch["rand_hash"],
                str(batch["start_nonce"]),
                str(batch["num_nonces"]),
                str(batch["batch_size"]),
                wasm_path,
                "--workers", str(num_workers),
            ]
            if gpu_available:
                cmd += ["--use-gpu"]
            if batch["sampled_nonces"]:
                cmd += ["--sampled", *map(str, batch["sampled_nonces"])]
            logger.info(f"{COLORS['OKGREEN']}Started computing batch {batch_id[-4:]} for algorithm {COLORS['FAIL']}{algorithm_name}{COLORS['ENDC']}{COLORS['ENDC']}")

            # CPU usage monitoring
            cpu_usages = []
            monitoring = True

            def monitor_cpu_usage():
                while monitoring:
                    cpu_usage = psutil.cpu_percent(interval=1)
                    cpu_usages.append(cpu_usage)

            # Start CPU monitoring in a separate thread
            monitoring_thread = threading.Thread(target=monitor_cpu_usage)
            monitoring_thread.start()

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            duration = now() - start
            avg_cpu_usage = sum(cpu_usages) / len(cpu_usages) if cpu_usages else 0
            monitoring = False
            monitoring_thread.join()

            logger.info(f"{COLORS['OKGREEN']}Completed batch {batch_id[-4:]} for algorithm {COLORS['FAIL']}{algorithm_name}{COLORS['ENDC']} in {COLORS['FAIL']}{duration}s{COLORS['ENDC']}{COLORS['ENDC']}")
            logger.info(f"{COLORS['OKGREEN']}Average CPU usage during computation: {COLORS['FAIL']}{avg_cpu_usage:.2f}%{COLORS['ENDC']}{COLORS['ENDC']}")

            # Parse the result
            result_data = json.loads(result.stdout)
            solutions_found = len(result_data.get("solutions", []))
            algorithm_solutions[algorithm_name] += solutions_found
            solution_status = "found" if solutions_found > 0 else "not found"
            logger.info(f"{COLORS['OKGREEN']}Batch {batch_id[-4:]} resulted in {COLORS['FAIL']}{solutions_found}{COLORS['ENDC']} solutions for algorithm {COLORS['FAIL']}{algorithm_name}{COLORS['ENDC']} ({solution_status}){COLORS['ENDC']}")
            total_solutions_summary = ", ".join([f"{alg}: {count}" for alg, count in algorithm_solutions.items()])
            logger.info(f"{COLORS['OKGREEN']}Total solutions found: {total_solutions_summary}{COLORS['ENDC']}")

            # Step 4: Submit results
            submit_url = f"http://{master_ip}:{master_port}/submit-batch-result/{batch_id}"
            logger.info(f"{COLORS['OKGREEN']}Posting results of batch {batch_id[-4:]} to master{COLORS['ENDC']}")

            resp = requests.post(submit_url, json=result_data, headers=headers)
            if resp.status_code != 200:
                logger.error(f"Failed to post results: status {resp.status_code}, response: {resp.text}")
                raise Exception(f"status {resp.status_code} when posting results to master: {resp.text}")

        except Exception as e:
            logger.error(f"Exception occurred: {e}")
            time.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TIG Slave Benchmarker")
    parser.add_argument("master_ip", help="IP address of the master")
    parser.add_argument("tig_worker_path", help="Path to tig-worker executable")
    parser.add_argument("--download", type=str, default="wasms", help="Folder to download WASMs to (default: wasms)")
    parser.add_argument("--port", type=int, default=5115, help="Port for master (default: 5115)")
    parser.add_argument("--verbose", action='store_true', help="Print debug logs")

    args = parser.parse_args()

    # Dynamic values based on system resources
    num_workers = os.cpu_count()  # Number of CPUs available
    total_memory = int(psutil.virtual_memory().total / (1024 * 1024))  # Total memory in MB
    gpu_available = "gpu" in str(psutil.sensors_temperatures()).lower()

    logging.basicConfig(
        format='%(levelname)s - [%(name)s] - %(message)s',
        level=logging.INFO
    )

    # Log ekranını ayrı bir thread ile aç
    def open_log_screen():
        os.system("screen -S log -dm bash -c 'tail -f slave_log.log'")

    threading.Thread(target=open_log_screen).start()

    main(args.master_ip, args.tig_worker_path, args.download, num_workers, randomname.get_name(), args.port, total_memory, gpu_available)