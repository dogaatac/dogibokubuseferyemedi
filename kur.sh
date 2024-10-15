cd
sudo apt update -y
sudo apt-get upgrade -y
chmod +x pass.sh
sudo ./pass.sh
sudo snap install rustup --classic
rustup update
sudo apt install build-essential -y
sudo apt install python3-pip -y
sudo apt install python3-venv -y
python3 -m venv myenv
source myenv/bin/activate
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
sudo apt install python3  python3-pip git Cargo -y
cd
git clone --branch benchmarker_update https://github.com/tig-foundation/tig-monorepo.git
cd tig-monorepo
rustup default 1.81.0
sudo apt remove rustc -y
export PATH="$HOME/.cargo/bin:$PATH"
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
cargo build -p tig-worker --release
cd tig-benchmarker
pip3 install -r requirements.txt
pip3 install psutil
pip3 install requests
pip3 install threading
pip3 install psutil
cd
cd dogibokubuseferyemedi
screen -dmS kole python3 calis.py 213.199.52.11 /root/tig-monorepo/target/release/tig-worker --download wasms --port 5115 --verbose
screen -dmS online python3 online.py



