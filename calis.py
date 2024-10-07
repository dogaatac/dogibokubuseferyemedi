import argparse
import json
import os
import logging
import randomname
import requests
import subprocess
import time
import psutil

logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])

def now():
    return int(time.time() * 1000)

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
    if not os.path.exists(tig_worker_path):
        raise FileNotFoundError(f"tig-worker not found at path: {tig_worker_path}")
    os.makedirs(download_wasms_folder, exist_ok=True)

    headers = {
        "User-Agent": slave_name
    }

    while True:
        try:
            # Step 1: Query for job
            start = now()
            get_batch_url = f"http://{master_ip}:{master_port}/get-batch"
            logger.info(f"fetching job from {get_batch_url}")
            resp = requests.get(get_batch_url, headers=headers)
            if resp.status_code != 200:
                raise Exception(f"status {resp.status_code} when fetching job: {resp.text}")
            logger.debug(f"fetching job: took {now() - start}ms")
            batch = resp.json()
            batch_id = f"{batch['benchmark_id']}_{batch['start_nonce']}"
            logger.debug(f"batch {batch_id}: {batch}")

            # Step 2: Download WASM
            wasm_path = os.path.join(download_wasms_folder, f"{batch['settings']['algorithm_id']}.wasm")
            if not os.path.exists(wasm_path):
                start = now()
                logger.info(f"downloading WASM from {batch['download_url']}")
                resp = requests.get(batch['download_url'])
                if resp.status_code != 200:
                    raise Exception(f"status {resp.status_code} when downloading WASM: {resp.text}")
                with open(wasm_path, 'wb') as f:
                    f.write(resp.content)
                logger.debug(f"downloading WASM: took {now() - start}ms")
            logger.debug(f"WASM Path: {wasm_path}")

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
            logger.info(f"computing batch: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            result = json.loads(result.stdout)
            logger.info(f"computing batch took {now() - start}ms")
            logger.debug(f"batch result: {result}")

            # Step 4: Submit results
            start = now()
            submit_url = f"http://{master_ip}:{master_port}/submit-batch-result/{batch_id}"
            logger.info(f"posting results to {submit_url}")
            resp = requests.post(submit_url, json=result, headers=headers)
            if resp.status_code != 200:
                raise Exception(f"status {resp.status_code} when posting results to master: {resp.text}")
            logger.debug(f"posting results took {now() - start} seconds")

        except Exception as e:
            logger.error(e)
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
        level=logging.DEBUG if args.verbose else logging.INFO
    )

    main(args.master_ip, args.tig_worker_path, args.download, num_workers, randomname.get_name(), args.port, total_memory, gpu_available)