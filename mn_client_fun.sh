path=$(cat quic-path)
$path/out/Default/quic_client --v=1 --quiet  --host=10.0.0.2 --port=6121  https://www.example.org/test2 > client.log 
#./out/Default/quic_client  --v=1 --host=127.0.0.1 --port=6121  https://www.example.org/
