path=$(cat quic-path)
curdir=$(pwd)
mkdir -p $HOME/.pki/nssdb
#certutil -d $HOME/.pki/nssdb -N --empty-password
cd $path/net/tools/quic/certs
./generate-certs.sh
cd $path/net/tools/quic/certs/out
certutil -d sql:$HOME/.pki/nssdb -A -t "C,," -n nickname -i 2048-sha256-root.pem
cd $curdir
