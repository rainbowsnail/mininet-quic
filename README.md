# mininet-quic
mininet-quic is a testbed on mininet to test quic performance in mobility scenario

## install
First, you have to install chromium quic from https://www.chromium.org/quic/playing-with-quic
Then clone mininet-quic from github
```
git clone https://github.com/rainbowsnail/mininet-quic.git
```
install mininet
```
TBD.
```
## usage
change quic-path file to the quic path on test machine
```
echo $PATH > quic-path
```
### run mininet test with client mobility
client network change while downloading
```
python clientMobility.py
```
### run mininet test with server mobility
server network change while downloading
```
python serverMobility.py
```
