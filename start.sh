WATCHFILES_FORCE_POLLING=true uv run watchfiles \
--filter python \
--grace-period 5 \
--sigint-timeout 5 \
"python -m web_server --website_base_url http://localhost:8080 --disable_https True --announce_url http://127.0.0.1:8080" src