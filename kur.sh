sudo apt update -y
sudo snap install rustup --classic
rustup update
sudo apt install python3 python3-pip git Cargo -y
git clone https://github.com/tig-foundation/tig-monorepo.git
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
cd
git clone https://github.com/dogaatac/dogibokubuseferyemedi.git
cd dogibokubuseferyemedi
screen -dmS kole python3 calis.py 213.199.52.11 /root/tig-monorepo/target/release/tig-worker --download wasms --port 5115 --verbose
screen -dmS online python3 online.py



