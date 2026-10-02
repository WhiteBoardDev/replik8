WATCHFILES_FORCE_POLLING=true uv run watchfiles \
--filter python \
--grace-period 5 \
--sigint-timeout 5 \
"python -m web_server --disable_https True" src