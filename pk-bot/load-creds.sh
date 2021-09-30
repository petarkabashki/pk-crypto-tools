# stty -echoctl
# vault login $(cat ~/vault/pkbot.token.txt) 1> /dev/null
export VAULT_TOKEN="$(vault token create -field token -policy=pkbot-policy)"
# vault login $VAULT_TOKEN 1> /dev/null
vault login

# stty echoctl
# export kucoin_apiTest=$(vault kv get -field=test secret/pkbot/kucoin/api)
# export kucoin_apiKey=$(vault kv get -field=apiKey secret/pkbot/kucoin/api)
# export kucoin_apiSecret=$(vault kv get -field=secret secret/pkbot/kucoin/api)
# export kucoin_apiPassphrase=$(vault kv get -field=passphrase secret/pkbot/kucoin/api)

export binance_apiTest=$(vault kv get -field=test secret/pkbot/data/binance/api)
export binance_apiKey=$(vault kv get -field=apiKey secret/pkbot/data/binance/api)
export binance_apiSecret=$(vault kv get -field=secret secret/pkbot/data/binance/api)

# export ftx_apiTest=$(vault kv get -field=test secret/pkbot/ftx/api)
# export ftx_apiKey=$(vault kv get -field=apiKey secret/pkbot/ftx/api)
# export ftx_apiSecret=$(vault kv get -field=secret secret/pkbot/ftx/api)