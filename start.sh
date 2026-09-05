
mkdir -p ./.certs
if [ ! -f "./.certs/key.pem" ]; then
    openssl req -new -x509 -keyout .certs/key.pem -out .certs/cert.pem -days 365 -nodes
fi

uv run watchfiles "python -m debugpy --listen 0.0.0.0:5678 src/main.py"