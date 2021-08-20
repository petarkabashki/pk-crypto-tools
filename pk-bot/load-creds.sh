# stty -echoctl
vault login $(cat ~/vault/pkbot.token.txt) 1> /dev/null
# stty echoctl
export kucoin_apiTest=$(vault kv get -field=test secret/pkbot/kucoin/api)
export kucoin_apiKey=$(vault kv get -field=apiKey secret/pkbot/kucoin/api)
export kucoin_apiSecret=$(vault kv get -field=secret secret/pkbot/kucoin/api)
export kucoin_apiPassphrase=$(vault kv get -field=passphrase secret/pkbot/kucoin/api)