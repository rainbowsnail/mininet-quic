path=$(cat quic-path)
$path/out/Default/quic_server --v=1 --port=6121 --quic_response_cache_dir=/tmp/quic-data/www.example.org --certificate_file=$path/net/tools/quic/certs/out/leaf_cert.pem --key_file=$path/net/tools/quic/certs/out/leaf_cert.pkcs8
