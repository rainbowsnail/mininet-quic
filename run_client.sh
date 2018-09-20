path=$(cat quic-path)
ls $path
$path/out/Default/quic_client  --quiet --host=127.0.0.1 --port=6121  https://www.example.org/test2
#./out/Default/quic_client  --v=1 --host=127.0.0.1 --port=6121  https://www.example.org/
