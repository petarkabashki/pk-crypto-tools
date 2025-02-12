


Margin Endpoints — binance-connector documentation







[binance-connector](index.html)





* [Changelog](CHANGELOG.html)
* [Getting Started](getting_started.html)
* [Spot APIs](binance.spot.html)
  + [Auto Invest Endpoints](binance.spot.auto_invest.html)
  + [C2C Endpoints](binance.spot.c2c.html)
  + [Convert Endpoints](binance.spot.convert.html)
  + [Data Stream Endpoints](binance.spot.data_stream.html)
  + [Fiat Endpoints](binance.spot.fiat.html)
  + [Card Gift Endpoints](binance.spot.gift_card.html)
  + [Crypto Loans Endpoints](binance.spot.crypto_loan.html)
  + [Margin Endpoints](#)
    - [Margin Account Borrow/Repay (MARGIN)](#margin-account-borrow-repay-margin)
      * [`borrow_repay()`](#binance.spot.Spot.borrow_repay)
    - [Get All Margin Assets (MARKET\_DATA)](#get-all-margin-assets-market-data)
      * [`margin_all_assets()`](#binance.spot.Spot.margin_all_assets)
    - [Get All Margin Pairs (MARKET\_DATA)](#get-all-margin-pairs-market-data)
      * [`margin_all_pairs()`](#binance.spot.Spot.margin_all_pairs)
    - [Query Margin PriceIndex (MARKET\_DATA)](#query-margin-priceindex-market-data)
      * [`margin_pair_index()`](#binance.spot.Spot.margin_pair_index)
    - [Margin Account New Order (TRADE)](#margin-account-new-order-trade)
      * [`new_margin_order()`](#binance.spot.Spot.new_margin_order)
    - [Margin Account Cancel Order (TRADE)](#margin-account-cancel-order-trade)
      * [`cancel_margin_order()`](#binance.spot.Spot.cancel_margin_order)
    - [Get Transfer History (USER\_DATA)](#get-transfer-history-user-data)
      * [`margin_transfer_history()`](#binance.spot.Spot.margin_transfer_history)
    - [Query borrow/repay records in Margin account (USER\_DATA)](#query-borrow-repay-records-in-margin-account-user-data)
      * [`borrow_repay_record()`](#binance.spot.Spot.borrow_repay_record)
    - [Get Interest History (USER\_DATA)](#get-interest-history-user-data)
      * [`margin_interest_history()`](#binance.spot.Spot.margin_interest_history)
    - [Get Force Liquidation Record (USER\_DATA)](#get-force-liquidation-record-user-data)
      * [`margin_force_liquidation_record()`](#binance.spot.Spot.margin_force_liquidation_record)
    - [Query Cross Margin Account Details (USER\_DATA)](#query-cross-margin-account-details-user-data)
      * [`margin_account()`](#binance.spot.Spot.margin_account)
    - [Query Margin Account’s Order (USER\_DATA)](#query-margin-account-s-order-user-data)
      * [`margin_order()`](#binance.spot.Spot.margin_order)
    - [Query Margin Account’s Open Order (USER\_DATA)](#query-margin-account-s-open-order-user-data)
      * [`margin_open_orders()`](#binance.spot.Spot.margin_open_orders)
    - [Margin Account Cancel all Open Orders on a Symbol (USER\_DATA)](#margin-account-cancel-all-open-orders-on-a-symbol-user-data)
      * [`margin_open_orders_cancellation()`](#binance.spot.Spot.margin_open_orders_cancellation)
    - [Query Margin Account’s All Orders (USER\_DATA)](#query-margin-account-s-all-orders-user-data)
      * [`margin_all_orders()`](#binance.spot.Spot.margin_all_orders)
    - [Query Margin Account’s Trade List (USER\_DATA)](#query-margin-account-s-trade-list-user-data)
      * [`margin_my_trades()`](#binance.spot.Spot.margin_my_trades)
    - [Query Max Borrow (USER\_DATA)](#query-max-borrow-user-data)
      * [`margin_max_borrowable()`](#binance.spot.Spot.margin_max_borrowable)
    - [Query Max Transfer-Out Amount (USER\_DATA)](#query-max-transfer-out-amount-user-data)
      * [`margin_max_transferable()`](#binance.spot.Spot.margin_max_transferable)
    - [Query Isolated Margin Account Info (USER\_DATA)](#query-isolated-margin-account-info-user-data)
      * [`isolated_margin_account()`](#binance.spot.Spot.isolated_margin_account)
    - [Get All Isolated Margin Symbol(USER\_DATA)](#get-all-isolated-margin-symbol-user-data)
      * [`isolated_margin_all_pairs()`](#binance.spot.Spot.isolated_margin_all_pairs)
    - [Toggle BNB Burn On Spot Trade And Margin Interest (USER\_DATA)](#toggle-bnb-burn-on-spot-trade-and-margin-interest-user-data)
      * [`toggle_bnbBurn()`](#binance.spot.Spot.toggle_bnbBurn)
    - [Get BNB Burn Status (USER\_DATA)](#get-bnb-burn-status-user-data)
      * [`bnbBurn_status()`](#binance.spot.Spot.bnbBurn_status)
    - [Get Margin Interest Rate History (USER\_DATA)](#get-margin-interest-rate-history-user-data)
      * [`margin_interest_rate_history()`](#binance.spot.Spot.margin_interest_rate_history)
    - [Margin Account New OCO (TRADE)](#margin-account-new-oco-trade)
      * [`new_margin_oco_order()`](#binance.spot.Spot.new_margin_oco_order)
    - [Margin Account Cancel OCO (TRADE)](#margin-account-cancel-oco-trade)
      * [`cancel_margin_oco_order()`](#binance.spot.Spot.cancel_margin_oco_order)
    - [Query Margin Account’s OCO (USER\_DATA)](#query-margin-account-s-oco-user-data)
      * [`get_margin_oco_order()`](#binance.spot.Spot.get_margin_oco_order)
    - [Query Margin Account’s all OCO (USER\_DATA)](#query-margin-account-s-all-oco-user-data)
      * [`get_margin_oco_orders()`](#binance.spot.Spot.get_margin_oco_orders)
    - [Query Margin Account’s Open OCO (USER\_DATA)](#query-margin-account-s-open-oco-user-data)
      * [`get_margin_open_oco_orders()`](#binance.spot.Spot.get_margin_open_oco_orders)
    - [Disable Isolated Margin Account (TRADE)](#disable-isolated-margin-account-trade)
      * [`cancel_isolated_margin_account()`](#binance.spot.Spot.cancel_isolated_margin_account)
    - [Enable Isolated Margin Account (TRADE)](#enable-isolated-margin-account-trade)
      * [`enable_isolated_margin_account()`](#binance.spot.Spot.enable_isolated_margin_account)
    - [Query Enabled Isolated Margin Account Limit (USER\_DATA)](#query-enabled-isolated-margin-account-limit-user-data)
      * [`isolated_margin_account_limit()`](#binance.spot.Spot.isolated_margin_account_limit)
    - [Query Cross Margin Fee Data (USER\_DATA)](#query-cross-margin-fee-data-user-data)
      * [`margin_fee()`](#binance.spot.Spot.margin_fee)
    - [Query Isolated Margin Fee Data (USER\_DATA)](#query-isolated-margin-fee-data-user-data)
      * [`isolated_margin_fee()`](#binance.spot.Spot.isolated_margin_fee)
    - [Query Isolated Margin Tier Data (USER\_DATA)](#query-isolated-margin-tier-data-user-data)
      * [`isolated_margin_tier()`](#binance.spot.Spot.isolated_margin_tier)
    - [Query Current Margin Order Count Usage (TRADE)](#query-current-margin-order-count-usage-trade)
      * [`margin_order_usage()`](#binance.spot.Spot.margin_order_usage)
    - [Get Summary of Margin account (USER\_DATA)](#get-summary-of-margin-account-user-data)
      * [`summary_of_margin_account()`](#binance.spot.Spot.summary_of_margin_account)
    - [Cross margin collateral ratio (MARKET\_DATA)](#cross-margin-collateral-ratio-market-data)
      * [`cross_margin_collateral_ratio()`](#binance.spot.Spot.cross_margin_collateral_ratio)
    - [Get Small Liability Exchange Coin List (USER\_DATA)](#get-small-liability-exchange-coin-list-user-data)
      * [`get_small_liability_exchange_coin_list()`](#binance.spot.Spot.get_small_liability_exchange_coin_list)
    - [Get Small Liability Exchange History (USER\_DATA)](#get-small-liability-exchange-history-user-data)
      * [`get_small_liability_exchange_history()`](#binance.spot.Spot.get_small_liability_exchange_history)
    - [Get a future hourly interest rate (USER\_DATA)](#get-a-future-hourly-interest-rate-user-data)
      * [`get_a_future_hourly_interest_rate()`](#binance.spot.Spot.get_a_future_hourly_interest_rate)
    - [Adjust cross margin max leverage (USER\_DATA)](#adjust-cross-margin-max-leverage-user-data)
      * [`adjust_cross_margin_max_leverage()`](#binance.spot.Spot.adjust_cross_margin_max_leverage)
    - [Query Margin Available Inventory (USER\_DATA)](#query-margin-available-inventory-user-data)
      * [`margin_available_inventory()`](#binance.spot.Spot.margin_available_inventory)
    - [Margin manual liquidation (MARGIN)](#margin-manual-liquidation-margin)
      * [`margin_manual_liquidation()`](#binance.spot.Spot.margin_manual_liquidation)
    - [Margin Account New OTO (TRADE)](#margin-account-new-oto-trade)
      * [`margin_new_oto_order()`](#binance.spot.Spot.margin_new_oto_order)
    - [Margin Account New OTOCO (TRADE)](#margin-account-new-otoco-trade)
      * [`margin_new_otoco_order()`](#binance.spot.Spot.margin_new_otoco_order)
    - [Query Liability Coin Leverage Bracket in Cross Margin Pro Mode(MARKET\_DATA)](#query-liability-coin-leverage-bracket-in-cross-margin-pro-mode-market-data)
      * [`liability_coin_leverage_bracket()`](#binance.spot.Spot.liability_coin_leverage_bracket)
  + [Market Endpoints](binance.spot.market.html)
  + [Mining Endpoints](binance.spot.mining.html)
  + [NFT Endpoints](binance.spot.nft.html)
  + [Pay Endpoints](binance.spot.pay.html)
  + [Portfolio Margin Endpoints](binance.spot.portfolio_margin.html)
  + [Rebate Endpoints](binance.spot.rebate.html)
  + [Staking Endpoints](binance.spot.staking.html)
  + [Sub Account Endpoints](binance.spot.sub_account.html)
  + [Account / Trade Endpoints](binance.spot.trade.html)
  + [Wallet Endpoints](binance.spot.wallet.html)
  + [Simple Earn Endpoints](binance.spot.simple_earn.html)
* [Spot Websocket Streams](binance.websocket_stream.spot.html)
* [Spot Websocket API](binance.websocket_api.html)



[binance-connector](index.html)


* [Spot APIs](binance.spot.html)
* Margin Endpoints
* [View page source](_sources/binance.spot.margin.rst.txt)

---



Margin Endpoints[](#margin-endpoints "Link to this heading")
=============================================================

Margin Account Borrow/Repay (MARGIN)[](#margin-account-borrow-repay-margin "Link to this heading")
---------------------------------------------------------------------------------------------------

borrow\_repay(*self*, *asset: str*, *isIsolated: str*, *symbol: str*, *amount*, *type: str*, *\*\*kwargs*)[](#binance.spot.Spot.borrow_repay "Link to this definition")

Margin account borrow/repay (MARGIN)

Margin account borrow/repay(MARGIN)

POST /sapi/v1/margin/borrow-repay

<https://developers.binance.com/docs/margin_trading/borrow-and-repay/Margin-Account-Borrow-Repay>

Parameters:

* **asset** (*str*) – The asset being transferred, e.g., BTC.
* **isIsolated** (*str*) – for isolated margin or not,”TRUE”, “FALSE”, default “FALSE”.
* **symbol** (*str*) – isolated symbol
* **amount** (*float*)
* **type** (*str*) – BORROW or REPAY

Keyword Arguments:

**recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000





Get All Margin Assets (MARKET\_DATA)[](#get-all-margin-assets-market-data "Link to this heading")
--------------------------------------------------------------------------------------------------

margin\_all\_assets(*self*, *\*\*kwargs*)[](#binance.spot.Spot.margin_all_assets "Link to this definition")

Get All Margin Assets (MARKET\_DATA)

GET /sapi/v1/margin/allAssets

<https://developers.binance.com/docs/margin_trading/market-data/Get-All-Margin-Assets>

Keyword Arguments:

**asset** (*str**,* *optional*)





Get All Margin Pairs (MARKET\_DATA)[](#get-all-margin-pairs-market-data "Link to this heading")
------------------------------------------------------------------------------------------------

margin\_all\_pairs(*self*, *\*\*kwargs*)[](#binance.spot.Spot.margin_all_pairs "Link to this definition")

Get All Margin Pairs (MARKET\_DATA)

GET /sapi/v1/margin/allPairs

<https://developers.binance.com/docs/margin_trading/market-data/Get-All-Cross-Margin-Pairs>

Keyword Arguments:

**symbol** (*str**,* *optional*)





Query Margin PriceIndex (MARKET\_DATA)[](#query-margin-priceindex-market-data "Link to this heading")
------------------------------------------------------------------------------------------------------

margin\_pair\_index(*self*, *symbol: str*, *\*\*kwargs*)[](#binance.spot.Spot.margin_pair_index "Link to this definition")

Query Margin PriceIndex (MARKET\_DATA)

GET /sapi/v1/margin/priceIndex

<https://developers.binance.com/docs/margin_trading/market-data/Query-Margin-PriceIndex>

Parameters:

**symbol** (*str*)





Margin Account New Order (TRADE)[](#margin-account-new-order-trade "Link to this heading")
-------------------------------------------------------------------------------------------

new\_margin\_order(*self*, *symbol: str*, *side: str*, *type: str*, *\*\*kwargs*)[](#binance.spot.Spot.new_margin_order "Link to this definition")

Margin Account New Order (TRADE)

Post a new order for margin account.

POST /sapi/v1/margin/order

<https://developers.binance.com/docs/margin_trading/trade/Margin-Account-New-Order>

Parameters:

* **symbol** (*str*)
* **side** (*str*) – BUY or SELL
* **type** (*str*)

Keyword Arguments:

* **quantity** (*float**,* *optional*)
* **quoteOrderQty** (*float**,* *optional*)
* **price** (*float**,* *optional*)
* **stopPrice** (*float**,* *optional*) – Used with STOP\_LOSS,STOP\_LOSS\_LIMIT,TAKE\_PROFIT and TAKE\_PROFIT\_LIMIT orders.
* **newClientOrderId** (*str**,* *optional*) – A unique id among open orders. Automatically generated if not sent.
* **icebergQty** (*float**,* *optional*) – Used with LIMIT, STOP\_LOSS\_LIMIT and TAKE\_PROFIT\_LIMIT to create an iceberg order.
* **newOrderRespType** (*str**,* *optional*) – Set the response JSON. ACK, RESULT or FULL;
  MARKET and LIMIT order types default to FULL, all other orders default to ACK.
* **sideEffectType** (*str**,* *optional*) – NO\_SIDE\_EFFECT, MARGIN\_BUY, AUTO\_REPAY,AUTO\_BORROW\_REPAY; default NO\_SIDE\_EFFECT.
* **timeInForce** (*str**,* *optional*) – GTC,IOC,FOK
* **isIsolated** (*str**,* *optional*) – for isolated margin or not,”TRUE”, “FALSE” default “FALSE”.
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Margin Account Cancel Order (TRADE)[](#margin-account-cancel-order-trade "Link to this heading")
-------------------------------------------------------------------------------------------------

cancel\_margin\_order(*self*, *symbol: str*, *\*\*kwargs*)[](#binance.spot.Spot.cancel_margin_order "Link to this definition")

Margin Account Cancel Order (TRADE)

> Cancel an active order for margin account.

DELETE /sapi/v1/margin/order

<https://developers.binance.com/docs/margin_trading/trade/Margin-Account-Cancel-Order>

Parameters:

**symbol** (*str*)


Keyword Arguments:

* **orderId** (*int**,* *optional*)
* **origClientOrderId** (*str**,* *optional*)
* **newClientOrderId** (*str**,* *optional*) – Used to uniquely identify this cancel. Automatically generated by default.
* **isIsolated** (*str**,* *optional*) – for isolated margin or not,”TRUE”, “FALSE”，default “FALSE”.
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Get Transfer History (USER\_DATA)[](#get-transfer-history-user-data "Link to this heading")
--------------------------------------------------------------------------------------------

margin\_transfer\_history(*self*, *asset: str*, *\*\*kwargs*)[](#binance.spot.Spot.margin_transfer_history "Link to this definition")

Get Cross Margin Transfer History (USER\_DATA)

GET /sapi/v1/margin/transfer

<https://developers.binance.com/docs/margin_trading/transfer/Get-Cross-Margin-Transfer-History>

Parameters:

**asset** (*str*)


Keyword Arguments:

* **type** (*str**,* *optional*) – Transfer Type: ROLL\_IN, ROLL\_OUT
* **startTime** (*int**,* *optional*)
* **endTime** (*int**,* *optional*)
* **current** (*int**,* *optional*) – Currently querying page. Start from 1. Default:1
* **size** (*int**,* *optional*) – Default:10 Max:100
* **isolatedSymbol** (*str**,* *optional*) – Symbol in Isolated Margin
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Query borrow/repay records in Margin account (USER\_DATA)[](#query-borrow-repay-records-in-margin-account-user-data "Link to this heading")
--------------------------------------------------------------------------------------------------------------------------------------------

borrow\_repay\_record(*self*, *type: str*, *\*\*kwargs*)[](#binance.spot.Spot.borrow_repay_record "Link to this definition")

Query borrow/repay records in Margin account (USER\_DATA)

GET /sapi/v1/margin/borrow-repay

<https://developers.binance.com/docs/margin_trading/borrow-and-repay/Query-Borrow-Repay>

Parameters:

**type** (*str*) – BORROW or REPAY


Keyword Arguments:

* **asset** (*str**,* *optional*)
* **isolatedSymbol** (*str**,* *optional*) – isolated symbol
* **txId** (*int**,* *optional*) – the tranId in POST /sapi/v1/margin/loan
* **startTime** (*int**,* *optional*)
* **endTime** (*int**,* *optional*)
* **current** (*int**,* *optional*) – Currently querying page. Start from 1. Default:1
* **size** (*int**,* *optional*) – Default:10 Max:100
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Get Interest History (USER\_DATA)[](#get-interest-history-user-data "Link to this heading")
--------------------------------------------------------------------------------------------

margin\_interest\_history(*self*, *\*\*kwargs*)[](#binance.spot.Spot.margin_interest_history "Link to this definition")

Get Interest History (USER\_DATA)

GET /sapi/v1/margin/interestHistory

<https://developers.binance.com/docs/margin_trading/borrow-and-repay/Get-Interest-History>

Keyword Arguments:

* **asset** (*str**,* *optional*)
* **isolatedSymbol** (*str**,* *optional*) – isolated symbol
* **startTime** (*int**,* *optional*)
* **endTime** (*int**,* *optional*)
* **current** (*int**,* *optional*) – Currently querying page. Start from 1. Default:1
* **size** (*int**,* *optional*) – Default:10 Max:100
* **archived** (*str**,* *optional*) – Default: false. Set to true for archived data from 6 months ago
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Get Force Liquidation Record (USER\_DATA)[](#get-force-liquidation-record-user-data "Link to this heading")
------------------------------------------------------------------------------------------------------------

margin\_force\_liquidation\_record(*self*, *\*\*kwargs*)[](#binance.spot.Spot.margin_force_liquidation_record "Link to this definition")

Get Force Liquidation Record (USER\_DATA)

GET /sapi/v1/margin/forceLiquidationRec

<https://developers.binance.com/docs/margin_trading/trade/Get-Force-Liquidation-Record>

Keyword Arguments:

* **isolatedSymbol** (*str**,* *optional*) – isolated symbol
* **startTime** (*int**,* *optional*)
* **endTime** (*int**,* *optional*)
* **current** (*int**,* *optional*) – Currently querying page. Start from 1. Default:1
* **size** (*int**,* *optional*) – Default:10 Max:100
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Query Cross Margin Account Details (USER\_DATA)[](#query-cross-margin-account-details-user-data "Link to this heading")
------------------------------------------------------------------------------------------------------------------------

margin\_account(*self*, *\*\*kwargs*)[](#binance.spot.Spot.margin_account "Link to this definition")

Query Cross Margin Account Details (USER\_DATA)

GET /sapi/v1/margin/account

<https://developers.binance.com/docs/margin_trading/account/Query-Cross-Margin-Account-Details>

Keyword Arguments:

**recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000





Query Margin Account’s Order (USER\_DATA)[](#query-margin-account-s-order-user-data "Link to this heading")
------------------------------------------------------------------------------------------------------------

margin\_order(*self*, *symbol: str*, *\*\*kwargs*)[](#binance.spot.Spot.margin_order "Link to this definition")

Query Margin Account’s Order (USER\_DATA)

GET /sapi/v1/margin/order

<https://developers.binance.com/docs/margin_trading/trade/Query-Margin-Account-Order>

Parameters:

**symbol** (*str*)


Keyword Arguments:

* **orderId** (*str**,* *optional*)
* **origClientOrderId** (*str**,* *optional*)
* **isIsolated** (*str**,* *optional*) – for isolated margin or not,”TRUE”, “FALSE”，default “FALSE”.
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Query Margin Account’s Open Order (USER\_DATA)[](#query-margin-account-s-open-order-user-data "Link to this heading")
----------------------------------------------------------------------------------------------------------------------

margin\_open\_orders(*self*, *\*\*kwargs*)[](#binance.spot.Spot.margin_open_orders "Link to this definition")

Query Margin Account’s Open Order (USER\_DATA)

GET /sapi/v1/margin/openOrders

<https://developers.binance.com/docs/margin_trading/trade/Query-Margin-Account-Open-Orders>

Keyword Arguments:

* **symbol** (*str**,* *optional*)
* **isIsolated** (*str**,* *optional*) – for isolated margin or not,”TRUE”, “FALSE”，default “FALSE”.
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Margin Account Cancel all Open Orders on a Symbol (USER\_DATA)[](#margin-account-cancel-all-open-orders-on-a-symbol-user-data "Link to this heading")
------------------------------------------------------------------------------------------------------------------------------------------------------

margin\_open\_orders\_cancellation(*self*, *symbol: str*, *\*\*kwargs*)[](#binance.spot.Spot.margin_open_orders_cancellation "Link to this definition")

Margin Account Cancel all Open Orders on a Symbol (USER\_DATA)

DELETE /sapi/v1/margin/openOrders

<https://developers.binance.com/docs/margin_trading/trade/Margin-Account-Cancel-All-Open-Orders>

Parameters:

**symbol** (*str*)


Keyword Arguments:

* **isIsolated** (*str**,* *optional*) – for isolated margin or not,”TRUE”, “FALSE”，default “FALSE”.
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Query Margin Account’s All Orders (USER\_DATA)[](#query-margin-account-s-all-orders-user-data "Link to this heading")
----------------------------------------------------------------------------------------------------------------------

margin\_all\_orders(*self*, *symbol: str*, *\*\*kwargs*)[](#binance.spot.Spot.margin_all_orders "Link to this definition")

Query Margin Account’s All Orders (USER\_DATA)

GET /sapi/v1/margin/allOrders

<https://developers.binance.com/docs/margin_trading/trade/Query-Margin-Account-All-Orders>

Parameters:

**symbol** (*str*)


Keyword Arguments:

* **orderId** (*int**,* *optional*)
* **isIsolated** (*str**,* *optional*) – for isolated margin or not,”TRUE”, “FALSE”，default “FALSE”.
* **startTime** (*int**,* *optional*)
* **endTime** (*int**,* *optional*)
* **limit** (*int**,* *optional*) – Default 500; max 500.
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Query Margin Account’s Trade List (USER\_DATA)[](#query-margin-account-s-trade-list-user-data "Link to this heading")
----------------------------------------------------------------------------------------------------------------------

margin\_my\_trades(*self*, *symbol: str*, *\*\*kwargs*)[](#binance.spot.Spot.margin_my_trades "Link to this definition")

Query Margin Account’s Trade List (USER\_DATA)

GET /sapi/v1/margin/myTrades

<https://developers.binance.com/docs/margin_trading/trade/Query-Margin-Account-Trade-List>

Parameters:

**symbol** (*str*)


Keyword Arguments:

* **fromID** (*int**,* *optional*) – TradeId to fetch from. Default gets most recent trades.
* **isIsolated** (*str**,* *optional*) – for isolated margin or not,”TRUE”, “FALSE”，default “FALSE”.
* **startTime** (*int**,* *optional*)
* **endTime** (*int**,* *optional*)
* **limit** (*int**,* *optional*) – Default 500; max 500.
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Query Max Borrow (USER\_DATA)[](#query-max-borrow-user-data "Link to this heading")
------------------------------------------------------------------------------------

margin\_max\_borrowable(*self*, *asset: str*, *\*\*kwargs*)[](#binance.spot.Spot.margin_max_borrowable "Link to this definition")

Query Max Borrow (USER\_DATA)

GET /sapi/v1/margin/maxBorrowable

<https://developers.binance.com/docs/margin_trading/borrow-and-repay/Query-Max-Borrow>

Parameters:

**asset** (*str*)


Keyword Arguments:

* **isolatedSymbol** (*str**,* *optional*) – isolated symbol
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Query Max Transfer-Out Amount (USER\_DATA)[](#query-max-transfer-out-amount-user-data "Link to this heading")
--------------------------------------------------------------------------------------------------------------

margin\_max\_transferable(*self*, *asset: str*, *\*\*kwargs*)[](#binance.spot.Spot.margin_max_transferable "Link to this definition")

Query Max Transfer-Out Amount (USER\_DATA)

GET /sapi/v1/margin/maxTransferable

<https://developers.binance.com/docs/margin_trading/transfer/Query-Max-Transfer-Out-Amount>

Parameters:

**asset** (*str*)


Keyword Arguments:

* **isolatedSymbol** (*str**,* *optional*) – isolated symbol
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Query Isolated Margin Account Info (USER\_DATA)[](#query-isolated-margin-account-info-user-data "Link to this heading")
------------------------------------------------------------------------------------------------------------------------

isolated\_margin\_account(*self*, *\*\*kwargs*)[](#binance.spot.Spot.isolated_margin_account "Link to this definition")

Query Isolated Margin Account Info (USER\_DATA)

GET /sapi/v1/margin/isolated/account

<https://developers.binance.com/docs/margin_trading/account/Query-Isolated-Margin-Account-Info>

Keyword Arguments:

* **symbols** (*str**,* *optional*) – Max 5 symbols can be sent; separated by “,”. e.g. “BTCUSDT,BNBUSDT,ADAUSDT”
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Get All Isolated Margin Symbol(USER\_DATA)[](#get-all-isolated-margin-symbol-user-data "Link to this heading")
---------------------------------------------------------------------------------------------------------------

isolated\_margin\_all\_pairs(*self*, *\*\*kwargs*)[](#binance.spot.Spot.isolated_margin_all_pairs "Link to this definition")

Get All Isolated Margin Symbol(USER\_DATA)

GET /sapi/v1/margin/isolated/allPairs

<https://developers.binance.com/docs/margin_trading/market-data/Get-All-Isolated-Margin-Symbol>

Keyword Arguments:

* **symbol** (*str**,* *optional*)
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Toggle BNB Burn On Spot Trade And Margin Interest (USER\_DATA)[](#toggle-bnb-burn-on-spot-trade-and-margin-interest-user-data "Link to this heading")
------------------------------------------------------------------------------------------------------------------------------------------------------

toggle\_bnbBurn(*self*, *\*\*kwargs*)[](#binance.spot.Spot.toggle_bnbBurn "Link to this definition")

Toggle BNB Burn On Spot Trade And Margin Interest (USER\_DATA)

POST /sapi/v1/bnbBurn

<https://developers.binance.com/docs/margin_trading/account/Toggle-BNB-Burn-On-Spot-Trade-And-Margin-Interest>

Keyword Arguments:

* **spotBNBBurn** (*str**,* *optional*) – “true” or “false”; Determines whether to use BNB to pay for trading fees on SPOT
* **interestBNBBurn** (*str**,* *optional*) – “true” or “false”; Determines whether to use BNB to pay for margin loan’s interest
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Get BNB Burn Status (USER\_DATA)[](#get-bnb-burn-status-user-data "Link to this heading")
------------------------------------------------------------------------------------------

bnbBurn\_status(*self*, *\*\*kwargs*)[](#binance.spot.Spot.bnbBurn_status "Link to this definition")

Get BNB Burn Status (USER\_DATA)

GET /sapi/v1/bnbBurn

<https://developers.binance.com/docs/margin_trading/account/Get-BNB-Burn-Status>

Keyword Arguments:

**recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000





Get Margin Interest Rate History (USER\_DATA)[](#get-margin-interest-rate-history-user-data "Link to this heading")
--------------------------------------------------------------------------------------------------------------------

margin\_interest\_rate\_history(*self*, *asset: str*, *\*\*kwargs*)[](#binance.spot.Spot.margin_interest_rate_history "Link to this definition")

Get Margin Interest Rate History (USER\_DATA)

GET /sapi/v1/margin/interestRateHistory

<https://developers.binance.com/docs/margin_trading/borrow-and-repay/Query-Margin-Interest-Rate-History>

Parameters:

**asset** (*str*)


Keyword Arguments:

* **vipLevel** (*str**,* *optional*) – Default: user’s vip level
* **startTime** (*int**,* *optional*) – Default: 7 days ago.
* **endTime** (*int**,* *optional*) – Default: present. Maximum range: 1 month.
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Margin Account New OCO (TRADE)[](#margin-account-new-oco-trade "Link to this heading")
---------------------------------------------------------------------------------------

new\_margin\_oco\_order(*self*, *symbol: str*, *side: str*, *quantity: float*, *price: float*, *stopPrice: float*, *\*\*kwargs*)[](#binance.spot.Spot.new_margin_oco_order "Link to this definition")

Margin Account New OCO (TRADE)

Send in a new OCO for a margin account

POST /sapi/v1/margin/order/oco

<https://developers.binance.com/docs/margin_trading/trade/Margin-Account-New-OCO>

Parameters:

* **symbol** (*str*)
* **side** (*str*)
* **quantity** (*float*)
* **price** (*float*)
* **stopPrice** (*float*)

Keyword Arguments:

* **isIsolated** (*str**,* *optional*) – For isolated margin or not “TRUE”, “FALSE”，default “FALSE”
* **listClientOrderId** (*str**,* *optional*) – A unique Id for the entire orderList
* **limitClientOrderId** (*str**,* *optional*) – A unique Id for the limit order
* **limitIcebergQty** (*float**,* *optional*)
* **stopClientOrderId** (*str**,* *optional*) – A unique Id for the stop loss/stop loss limit leg
* **stopLimitPrice** (*float**,* *optional*) – If provided, stopLimitTimeInForce is required
* **stopIcebergQty** (*float**,* *optional*)
* **stopLimitTimeInForce** (*str**,* *optional*) – Valid values are GTC/FOK/IOC
* **newOrderRespType** (*str**,* *optional*) – Set the response JSON
* **sideEffectType** (*str**,* *optional*) – NO\_SIDE\_EFFECT, MARGIN\_BUY, AUTO\_REPAY,AUTO\_BORROW\_REPAY; default NO\_SIDE\_EFFECT
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Margin Account Cancel OCO (TRADE)[](#margin-account-cancel-oco-trade "Link to this heading")
---------------------------------------------------------------------------------------------

cancel\_margin\_oco\_order(*self*, *symbol*, *orderListId: int = None*, *listClientOrderId: str = None*, *\*\*kwargs*)[](#binance.spot.Spot.cancel_margin_oco_order "Link to this definition")

Margin Account Cancel OCO (TRADE)

Cancel an entire Order List for a margin account.

DELETE /sapi/v1/margin/orderList

<https://developers.binance.com/docs/margin_trading/trade/Margin-Account-Cancel-OCO>

Parameters:

* **symbol** (*str*)
* **orderListId** (*int**,* *optional*) – Either orderListId or listClientOrderId must be provided
* **listClientOrderId** (*str**,* *optional*) – Either orderListId or listClientOrderId must be provided

Keyword Arguments:

* **isIsolated** (*str**,* *optional*) – For isolated margin or not “TRUE”, “FALSE”，default “FALSE”
* **newClientOrderId** (*str**,* *optional*) – Used to uniquely identify this cancel. Automatically generated by default.
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Query Margin Account’s OCO (USER\_DATA)[](#query-margin-account-s-oco-user-data "Link to this heading")
--------------------------------------------------------------------------------------------------------

get\_margin\_oco\_order(*self*, *orderListId: int = None*, *origClientOrderId: str = None*, *\*\*kwargs*)[](#binance.spot.Spot.get_margin_oco_order "Link to this definition")

Query Margin Account’s OCO (USER\_DATA)

Retrieves a specific OCO based on provided optional parameters

GET /sapi/v1/margin/orderList

<https://developers.binance.com/docs/margin_trading/trade/Query-Margin-Account-OCO>

Parameters:

* **orderListId** (*int**,* *optional*) – Either orderListId or origClientOrderId must be provided
* **origClientOrderId** (*str**,* *optional*) – Either orderListId or origClientOrderId must be provided.

Keyword Arguments:

* **isIsolated** (*str**,* *optional*) – For isolated margin or not “TRUE”, “FALSE”，default “FALSE”
* **symbol** (*str**,* *optional*) – Mandatory for isolated margin, not supported for cross margin
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Query Margin Account’s all OCO (USER\_DATA)[](#query-margin-account-s-all-oco-user-data "Link to this heading")
----------------------------------------------------------------------------------------------------------------

get\_margin\_oco\_orders(*self*, *\*\*kwargs*)[](#binance.spot.Spot.get_margin_oco_orders "Link to this definition")

Query Margin Account’s all OCO (USER\_DATA)

Retrieves all OCO for a specific margin account based on provided optional parameters

GET /sapi/v1/margin/allOrderList

<https://developers.binance.com/docs/margin_trading/trade/Query-Margin-Account-All-OCO>

Keyword Arguments:

* **isIsolated** (*str**,* *optional*) – For isolated margin or not “TRUE”, “FALSE”，default “FALSE”
* **symbol** (*str**,* *optional*) – Mandatory for isolated margin, not supported for cross margin
* **fromId** (*int**,* *optional*) – If supplied, neither startTime or endTime can be provided
* **startTime** (*int**,* *optional*)
* **endTime** (*int**,* *optional*)
* **limit** (*int**,* *optional*) – Default Value: 500; Max Value: 1000
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Query Margin Account’s Open OCO (USER\_DATA)[](#query-margin-account-s-open-oco-user-data "Link to this heading")
------------------------------------------------------------------------------------------------------------------

get\_margin\_open\_oco\_orders(*self*, *\*\*kwargs*)[](#binance.spot.Spot.get_margin_open_oco_orders "Link to this definition")

Query Margin Account’s Open OCO (USER\_DATA)

GET /sapi/v1/margin/openOrderList

<https://developers.binance.com/docs/margin_trading/trade/Query-Margin-Account-Open-OCO>

Keyword Arguments:

* **isIsolated** (*str**,* *optional*) – For isolated margin or not “TRUE”, “FALSE” default “FALSE”
* **symbol** (*str**,* *optional*) – Mandatory for isolated margin, not supported for cross margin
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Disable Isolated Margin Account (TRADE)[](#disable-isolated-margin-account-trade "Link to this heading")
---------------------------------------------------------------------------------------------------------

cancel\_isolated\_margin\_account(*self*, *symbol: str*, *\*\*kwargs*)[](#binance.spot.Spot.cancel_isolated_margin_account "Link to this definition")

Disable Isolated Margin Account (TRADE)
Disable isolated margin account for a specific symbol. Each trading pair can only be deactivated once every 24 hours.

DELETE /sapi/v1/margin/isolated/account

<https://developers.binance.com/docs/margin_trading/account/Disable-Isolated-Margin-Account>

Parameters:

**symbol** (*str*)


Keyword Arguments:

**recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000





Enable Isolated Margin Account (TRADE)[](#enable-isolated-margin-account-trade "Link to this heading")
-------------------------------------------------------------------------------------------------------

enable\_isolated\_margin\_account(*self*, *symbol: str*, *\*\*kwargs*)[](#binance.spot.Spot.enable_isolated_margin_account "Link to this definition")

Enable Isolated Margin Account (TRADE)
Enable isolated margin account for a specific symbol (Only supports activation of previously disabled accounts).

POST /sapi/v1/margin/isolated/account

<https://developers.binance.com/docs/margin_trading/account/Enable-Isolated-Margin-Account>

Parameters:

**symbol** (*str*)


Keyword Arguments:

**recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000





Query Enabled Isolated Margin Account Limit (USER\_DATA)[](#query-enabled-isolated-margin-account-limit-user-data "Link to this heading")
------------------------------------------------------------------------------------------------------------------------------------------

isolated\_margin\_account\_limit(*self*, *\*\*kwargs*)[](#binance.spot.Spot.isolated_margin_account_limit "Link to this definition")

Query Enabled Isolated Margin Account Limit (USER\_DATA)
Query enabled isolated margin account limit.

GET /sapi/v1/margin/isolated/accountLimit

<https://developers.binance.com/docs/margin_trading/account/Query-Enabled-Isolated-Margin-Account-Limit>

Keyword Arguments:

**recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000





Query Cross Margin Fee Data (USER\_DATA)[](#query-cross-margin-fee-data-user-data "Link to this heading")
----------------------------------------------------------------------------------------------------------

margin\_fee(*self*, *\*\*kwargs*)[](#binance.spot.Spot.margin_fee "Link to this definition")

Query Cross Margin Fee Data (USER\_DATA)
Get cross margin fee data collection with any vip level or user’s current specific data as <https://www.binance.com/en/margin-fee>

GET /sapi/v1/margin/crossMarginData

<https://developers.binance.com/docs/margin_trading/account/Query-Cross-Margin-Fee-Data>

Keyword Arguments:

* **vipLevel** (*int**,* *optional*) – User’s current specific margin data will be returned if vipLevel is omitted
* **coin** (*str**,* *optional*)
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Query Isolated Margin Fee Data (USER\_DATA)[](#query-isolated-margin-fee-data-user-data "Link to this heading")
----------------------------------------------------------------------------------------------------------------

isolated\_margin\_fee(*self*, *\*\*kwargs*)[](#binance.spot.Spot.isolated_margin_fee "Link to this definition")

Query Isolated Margin Fee Data (USER\_DATA)
Get isolated margin fee data collection with any vip level or user’s current specific data as <https://www.binance.com/en/margin-fee>

GET /sapi/v1/margin/isolatedMarginData

<https://developers.binance.com/docs/margin_trading/account/Query-Isolated-Margin-Fee-Data>

Keyword Arguments:

* **vipLevel** (*int**,* *optional*) – User’s current specific margin data will be returned if vipLevel is omitted
* **symbol** (*str**,* *optional*)
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Query Isolated Margin Tier Data (USER\_DATA)[](#query-isolated-margin-tier-data-user-data "Link to this heading")
------------------------------------------------------------------------------------------------------------------

isolated\_margin\_tier(*self*, *symbol: str*, *\*\*kwargs*)[](#binance.spot.Spot.isolated_margin_tier "Link to this definition")

Query Isolated Margin Tier Data (USER\_DATA)
Get isolated margin tier data collection with any tier as <https://www.binance.com/en/margin-data>

GET /sapi/v1/margin/isolatedMarginTier

<https://developers.binance.com/docs/margin_trading/market-data/Query-Isolated-Margin-Tier-Data>

Parameters:

**symbol** (*str*)


Keyword Arguments:

* **tier** (*int**,* *optional*) – All margin tier data will be returned if tier is omitted
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Query Current Margin Order Count Usage (TRADE)[](#query-current-margin-order-count-usage-trade "Link to this heading")
-----------------------------------------------------------------------------------------------------------------------

margin\_order\_usage(*self*, *\*\*kwargs*)[](#binance.spot.Spot.margin_order_usage "Link to this definition")

Query Current Margin Order Count Usage (TRADE)
Displays the user’s current margin order count usage for all intervals.

GET /sapi/v1/margin/rateLimit/order

<https://developers.binance.com/docs/margin_trading/trade/Query-Current-Margin-Order-Count-Usage>

Keyword Arguments:

* **isIsolated** (*str**,* *optional*) – for isolated margin or not, “TRUE”, “FALSE”, default “FALSE”
* **symbol** (*str**,* *optional*) – isolated symbol, mandatory for isolated margin
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Get Summary of Margin account (USER\_DATA)[](#get-summary-of-margin-account-user-data "Link to this heading")
--------------------------------------------------------------------------------------------------------------

summary\_of\_margin\_account(*self*, *\*\*kwargs*)[](#binance.spot.Spot.summary_of_margin_account "Link to this definition")

Get Summary of Margin account (USER\_DATA)
Get personal margin level information

GET /sapi/v1/margin/tradeCoeff

<https://developers.binance.com/docs/margin_trading/account/Get-Summary-Of-Margin-Account>

Keyword Arguments:

**recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000





Cross margin collateral ratio (MARKET\_DATA)[](#cross-margin-collateral-ratio-market-data "Link to this heading")
------------------------------------------------------------------------------------------------------------------

cross\_margin\_collateral\_ratio(*self*)[](#binance.spot.Spot.cross_margin_collateral_ratio "Link to this definition")

Cross margin collateral ratio (MARKET\_DATA)

Weight(IP): 100

GET /sapi/v1/margin/crossMarginCollateralRatio

<https://developers.binance.com/docs/margin_trading/market-data/Cross-margin-collateral-ratio>



Get Small Liability Exchange Coin List (USER\_DATA)[](#get-small-liability-exchange-coin-list-user-data "Link to this heading")
--------------------------------------------------------------------------------------------------------------------------------

get\_small\_liability\_exchange\_coin\_list(*self*, *\*\*kwargs*)[](#binance.spot.Spot.get_small_liability_exchange_coin_list "Link to this definition")

Get Small Liability Exchange Coin List (USER\_DATA)

Query the coins which can be small liability exchange

Weight(UID): 100

GET /sapi/v1/margin/exchange-small-liability

<https://developers.binance.com/docs/margin_trading/trade/Get-Small-Liability-Exchange-Coin-List>

Keyword Arguments:

**recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000





Get Small Liability Exchange History (USER\_DATA)[](#get-small-liability-exchange-history-user-data "Link to this heading")
----------------------------------------------------------------------------------------------------------------------------

get\_small\_liability\_exchange\_history(*self*, *current: int*, *size: int*, *\*\*kwargs*)[](#binance.spot.Spot.get_small_liability_exchange_history "Link to this definition")

Get Small Liability Exchange History (USER\_DATA)

Get Small liability Exchange History

Weight(UID): 100

GET /sapi/v1/margin/exchange-small-liability-history

<https://developers.binance.com/docs/margin_trading/trade/Get-Small-Liability-Exchange-History>

Parameters:

* **current** (*int**,* *optional*) – Current querying page. Start from 1. Default:1
* **size** (*int**,* *optional*) – Default:10 Max:100

Keyword Arguments:

* **startTime** (*int**,* *optional*) – UTC timestamp in ms
* **endTime** (*int**,* *optional*) – UTC timestamp in ms
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Get a future hourly interest rate (USER\_DATA)[](#get-a-future-hourly-interest-rate-user-data "Link to this heading")
----------------------------------------------------------------------------------------------------------------------

get\_a\_future\_hourly\_interest\_rate(*self*, *assets: str*, *isIsolated: bool*, *\*\*kwargs*)[](#binance.spot.Spot.get_a_future_hourly_interest_rate "Link to this definition")

Get a future hourly interest rate (USER\_DATA)

Get user the next hourly estimate interest

Weight(UID): 100

GET /sapi/v1/margin/next-hourly-interest-rate

<https://developers.binance.com/docs/margin_trading/borrow-and-repay/Get-a-future-hourly-interest-rate>

Parameters:

* **assets** (*str**,* *optional*) – List of assets, separated by commas, up to 20
* **isIsolated** (*IsIsolated**,* *optional*) – for isolated margin or not, “TRUE”, “FALSE”

Keyword Arguments:

**recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000





Adjust cross margin max leverage (USER\_DATA)[](#adjust-cross-margin-max-leverage-user-data "Link to this heading")
--------------------------------------------------------------------------------------------------------------------

adjust\_cross\_margin\_max\_leverage(*self*, *maxLeverage: int*, *\*\*kwargs*)[](#binance.spot.Spot.adjust_cross_margin_max_leverage "Link to this definition")

Adjust cross margin max leverage (USER\_DATA)

Adjust cross margin max leverage

Weight(IP): 3000

POST /sapi/v1/margin/max-leverage

<https://developers.binance.com/docs/margin_trading/account/Adjust-Cross-Margin-Max-Leverage>

Parameters:

**maxLeverage** (*int*)


Keyword Arguments:

**recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000





Query Margin Available Inventory (USER\_DATA)[](#query-margin-available-inventory-user-data "Link to this heading")
--------------------------------------------------------------------------------------------------------------------

margin\_available\_inventory(*self*, *type: str*, *\*\*kwargs*)[](#binance.spot.Spot.margin_available_inventory "Link to this definition")

Query Margin Available Inventory (USER\_DATA)

GET /sapi/v1/margin/available-inventory

<https://developers.binance.com/docs/margin_trading/market-data/Query-margin-avaliable-inventory>

Parameters:

**type** (*str*) – “MARGIN”, “ISOLATED”


Keyword Arguments:

**recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000





Margin manual liquidation (MARGIN)[](#margin-manual-liquidation-margin "Link to this heading")
-----------------------------------------------------------------------------------------------

margin\_manual\_liquidation(*self*, *type: str*, *\*\*kwargs*)[](#binance.spot.Spot.margin_manual_liquidation "Link to this definition")

Margin manual liquidation (MARGIN)

POST /sapi/v1/margin/manual-liquidation

<https://developers.binance.com/docs/margin_trading/trade/Margin-Manual-Liquidation>

Parameters:

**type** (*str*) – “MARGIN”, “ISOLATED”


Keyword Arguments:

* **symbol** (*str**,* *optional*) – When type selects ISOLATED, symbol must be filled in
* **recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000




Margin Account New OTO (TRADE)[](#margin-account-new-oto-trade "Link to this heading")
---------------------------------------------------------------------------------------

margin\_new\_oto\_order(*self*, *symbol: str*, *workingType: str*, *workingSide: str*, *workingPrice: float*, *workingQuantity: float*, *pendingType: str*, *pendingSide: str*, *pendingQuantity: float*, *\*\*kwargs*)[](#binance.spot.Spot.margin_new_oto_order "Link to this definition")

Margin Account New OTO (TRADE)

Post a new OTOCO order for margin account

Weight(UID): 6

POST /sapi/v1/margin/order/oto

<https://developers.binance.com/docs/margin_trading/trade/Margin-Account-New-OTO>

Parameters:

* **symbol** (*str*)
* **workingType** (*str*)
* **workingSide** (*str*)
* **workingPrice** (*float*)
* **workingQuantity** (*float*)
* **pendingType** (*str*)
* **pendingSide** (*str*)
* **pendingQuantity** (*float*)

Keyword Arguments:

* **isIsolated** (*str**,* *optional*) – for isolated margin or not: “TRUE”, “FALSE”. Default: “FALSE”
* **listClientOrderId** (*str**,* *optional*) – Arbitrary unique ID among open order lists. Automatically generated if not sent. A new order list with the same listClientOrderId is accepted only when the previous one is filled or completely expired. listClientOrderId is distinct from the workingClientOrderId and the pendingClientOrderId.
* **newOrderRespType** (*str**,* *optional*) – Set the response JSON. ACK, RESULT, or FULL; MARKET and LIMIT order types default to FULL, all other orders default to ACK.
* **sideEffectType** (*str**,* *optional*) – NO\_SIDE\_EFFECT, MARGIN\_BUY, AUTO\_REPAY or AUTO\_BORROW\_REPAY
* **selfTradePreventionMode** (*str**,* *optional*) – The allowed enums is dependent on what is configured on the symbol. The possible supported values are EXPIRE\_TAKER, EXPIRE\_MAKER, EXPIRE\_BOTH, NONE
* **autoRepayAtCancel** (*bool**,* *optional*) – Only when MARGIN\_BUY order takes effect, true means that the debt generated by the order needs to be repay after the order is cancelled. The default is true
* **workingClientOrderId** (*str**,* *optional*) – Arbitrary unique ID among open orders for the working order. Automatically generated if not sent.
* **workingIcebergQty** (*float**,* *optional*) – This can only be used if workingTimeInForce is GTC.
* **workingTimeInForce** (*str**,* *optional*) – GTC, IOC or FOK
* **pendingClientOrderId** (*str**,* *optional*) – Arbitrary unique ID among open orders for the pending order. Automatically generated if not sent.
* **pendingPrice** (*float**,* *optional*)
* **pendingStopPrice** (*float**,* *optional*)
* **pendingTrailingDelta** (*float**,* *optional*)
* **pendingIcebergQty** (*float**,* *optional*) – This can only be used if pendingTimeInForce is GTC.
* **pendingTimeInForce** (*str**,* *optional*) – GTC, IOC or FOK




Margin Account New OTOCO (TRADE)[](#margin-account-new-otoco-trade "Link to this heading")
-------------------------------------------------------------------------------------------

margin\_new\_otoco\_order(*self*, *symbol: str*, *workingType: str*, *workingSide: str*, *workingPrice: float*, *workingQuantity: float*, *pendingSide: str*, *pendingQuantity: float*, *pendingAboveType: str*, *\*\*kwargs*)[](#binance.spot.Spot.margin_new_otoco_order "Link to this definition")

Margin Account New OTOCO (TRADE)

Post a new OTOCO order for margin account

Weight(UID): 6

POST /sapi/v1/margin/order/otoco

<https://developers.binance.com/docs/margin_trading/trade/Margin-Account-New-OTOCO>

Parameters:

* **symbol** (*str*)
* **workingType** (*str*)
* **workingSide** (*str*)
* **workingPrice** (*float*)
* **workingQuantity** (*float*)
* **pendingSide** (*str*)
* **pendingQuantity** (*float*)
* **pendingAboveType** (*str*)

Keyword Arguments:

* **isIsolated** (*str**,* *optional*) – for isolated margin or not: “TRUE”, “FALSE”. Default: “FALSE”
* **sideEffectType** (*str**,* *optional*) – NO\_SIDE\_EFFECT, MARGIN\_BUY, AUTO\_REPAY or AUTO\_BORROW\_REPAY
* **autoRepayAtCancel** (*bool**,* *optional*) – Only when MARGIN\_BUY order takes effect, true means that the debt generated by the order needs to be repay after the order is cancelled. The default is true
* **listClientOrderId** (*str**,* *optional*) – Arbitrary unique ID among open order lists. Automatically generated if not sent. A new order list with the same listClientOrderId is accepted only when the previous one is filled or completely expired. listClientOrderId is distinct from the workingClientOrderId, pendingAboveClientOrderId, and the pendingBelowClientOrderId.
* **newOrderRespType** (*str**,* *optional*) – Format of the JSON response.
* **selfTradePreventionMode** (*str**,* *optional*) – The allowed enums is dependent on what is configured on the symbol. The possible supported values are EXPIRE\_TAKER, EXPIRE\_MAKER, EXPIRE\_BOTH, NONE
* **workingClientOrderId** (*str**,* *optional*) – Arbitrary unique ID among open orders for the working order. Automatically generated if not sent.
* **workingIcebergQty** (*float**,* *optional*) – This can only be used if workingTimeInForce is GTC.
* **workingTimeInForce** (*str**,* *optional*) – GTC, IOC or FOK
* **pendingAboveClientOrderId** (*str**,* *optional*) – Arbitrary unique ID among open orders for the pending above order. Automatically generated if not sent.
* **pendingAbovePrice** (*float**,* *optional*)
* **pendingAboveStopPrice** (*float**,* *optional*)
* **pendingAboveTrailingDelta** (*float**,* *optional*)
* **pendingAboveIcebergQty** (*float**,* *optional*) – This can only be used if pendingAboveTimeInForce is GTC.
* **pendingAboveTimeInForce** (*str**,* *optional*)
* **pendingBelowType** (*str**,* *optional*) – Supported values: LIMIT\_MAKER, STOP\_LOSS, and STOP\_LOSS\_LIMIT
* **pendingBelowClientOrderId** (*str**,* *optional*) – Arbitrary unique ID among open orders for the pending below order. Automatically generated if not sent.
* **pendingBelowPrice** (*float**,* *optional*)
* **pendingBelowStopPrice** (*float**,* *optional*)
* **pendingBelowTrailingDelta** (*float**,* *optional*)
* **pendingBelowIcebergQty** (*float**,* *optional*) – This can only be used if pendingBelowTimeInForce is GTC.
* **pendingBelowTimeInForce** (*str**,* *optional*)




Query Liability Coin Leverage Bracket in Cross Margin Pro Mode(MARKET\_DATA)[](#query-liability-coin-leverage-bracket-in-cross-margin-pro-mode-market-data "Link to this heading")
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

liability\_coin\_leverage\_bracket(*self*, *\*\*kwargs*)[](#binance.spot.Spot.liability_coin_leverage_bracket "Link to this definition")

Query Liability Coin Leverage Bracket in Cross Margin Pro Mode(MARKET\_DATA)

GET /sapi/v1/margin/leverageBracket

<https://developers.binance.com/docs/margin_trading/market-data/Query-Liability-Coin-Leverage-Bracket-in-Cross-Margin-Pro-Mode>

Keyword Arguments:

**recvWindow** (*int**,* *optional*) – The value cannot be greater than 60000








 [Previous](binance.spot.crypto_loan.html "Crypto Loans Endpoints")
[Next](binance.spot.market.html "Market Endpoints") 

---


© Copyright 2023, binance.


Built with [Sphinx](https://www.sphinx-doc.org/) using a
[theme](https://github.com/readthedocs/sphinx_rtd_theme)
provided by [Read the Docs](https://readthedocs.org).






