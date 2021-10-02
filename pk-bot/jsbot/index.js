require('dotenv').config();
const fs = require('fs')
const { MongoClient } = require("mongodb");

const Binance = require('node-binance-api');
const binance = new Binance().options({
    APIKEY: process.env.BINANCE_API_KEY,
    APISECRET: process.env.BINANCE_API_SECRET
});

global.tickers = {};

// binance.marketBuy('ALGOUSDT', 50);

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

// function roundit(x, decimals) {
//     z = Math.pow(10, decimals);
//     return 
// }
const qtyDecimals = {
    'ATOMUSDT' : 2,
    'LUNAUSDT' : 2,
    'EGLDUSD': 2
};

(async () => {

    // const dateFormat = require('dateformat')
    const dateFormatModule = await import('dateformat')
    const dateFormat = dateFormatModule.default;


    // dateFormat(new Date(), "yyyy-mm-dd h:MM:ss");

    // const storeData = (data, path) => {
    //     try {
    //         fs.writeFileSync(path, JSON.stringify(data))
    //     } catch (err) {
    //         console.error(err)
    //     }
    // }
    // const loadData = (path) => {
    //     try {
    //         return fs.readFileSync(path, 'utf8')
    //     } catch (err) {
    //         console.error(err)
    //         return false
    //     }
    // }



    const uri = "mongodb://localhost:27017";
    const client = new MongoClient(uri);

    await client.connect();
    db = client.db('jsbot');
    orders = db.collection('orders')

    // positionSize = 100;

    // liveOrders = await orders.find({"status": "live"})
    // let liveOrdersRes = await orders.aggregate([{
    //     $match: { status: "live" }
    // }])

    binance.websockets.miniTicker(tickers => { global.tickers = { ...global.tickers, ...tickers }; });

// BUY IF PRICE BELOW TRIGGER
    setInterval(async () => {

        const liveOrdersCursor = await orders.aggregate([{
            $match: { status: { $in: ['buy', 'buyat'] } }
        }]);
        const liveOrders = await liveOrdersCursor.toArray();

        console.log(dateFormat())
        liveOrders.forEach(async order => {
            try {
                ticker = global.tickers[order.symbol]
                if (!ticker) return;
    
                if (
                        (order.status === 'buy')  ||
                        (order.status == 'buyat' && ticker.close <= order.trigger)
                    
                    ) {
                    // console.log(`${order.symbol}`)
                    const amount = order.qty || (order.size / Number(ticker.close)).toFixed(qtyDecimals[order.symbol]); 
                    console.log(`   Buying: ${order.id} / ${amount}  ${order.symbol} @ ${ticker.close}`);
                    orderResp = await binance.marketBuy(order.symbol, amount);

                    const buyCommission = orderResp.fills.reduce( (a,x) => a + x.commission, 0);
                    const totalPaid = orderResp.fills.reduce( (a,x) => a + x.qty * x.price, 0);
                    const qty = orderResp.fills.reduce( (a,x) => a + x.qty, 0);
                    const avgBuyPrice = (totalPaid / qty).toFixed(qtyDecimals[order.symbol])

                    const updRes = await orders.updateOne({ _id: order._id }, { $set: {
                        status: "setstop",
                        qty: amount ,
                        avgBuyPrice,
                        buyResp: orderResp,
                        buyCommission,
                        qty,

                    }});
                }
            } catch(err) {
                console.error(`ERROR: ${order.id} / ${err.message}`);
                await orders.updateOne({ _id: order._id }, { $set: {
                    status: "err",
                    error: err.message
                }});
            }
        });
    }, 2000);

// SET STOPLOSS    
    setInterval(async () => {

        const boughtOrdersCursor = await orders.aggregate([{
            $match: { status: "setstop" }
        }]);
        const boughtOrders = await boughtOrdersCursor.toArray();

        console.log(dateFormat())
        boughtOrders.forEach(async order => {
            try {
                decimals = order.trigger.toString().split('.')[1].length

                if (order.stopResp && order.stopResp.orderId) { 
                    try {
                        console.log(`       Canceling previous stop order :  ${order.stopResp.orderId}`);
                        const cancelStopResp = await binance.cancel(order.symbol, order.stopResp.orderId);
        
                        const updRes = await orders.updateOne({ _id: order._id }, { $set: {
                            cancelStopResp: cancelStopResp,
                        }});
        
                    } catch {
                        console.error(`Error canceling stop order: ${order.id}`)
                    }
                }

                console.log(`   Setting stop: ${order.id} /  ${order.qty}  ${order.symbol} @ ${order.stop}`);
                orderResp = await binance.sell(order.symbol, order.qty, 
                    (order.stop * 0.99).toFixed(decimals), 
                    {stopPrice: order.stop, type: "STOP_LOSS_LIMIT"});
    
                const updRes = await orders.updateOne({ _id: order._id }, { $set: {
                    status: "sellat",
                    stopResp: orderResp
                }});
            } catch(err) {
                console.error(`ERROR: ${order.id} / ${err.message}`);
                await orders.updateOne({ _id: order._id }, { $set: {
                    status: "err",
                    error: err.message
                }});
            }
        
        });
    }, 1000);

// SELL
    setInterval(async () => {
        
        const boughtOrdersCursor = await orders.aggregate([{
            $match: { status: {$in: ['sell', 'sellat']} }
        }]);
        const boughtOrders = await boughtOrdersCursor.toArray();

        console.log(dateFormat())
        boughtOrders.forEach(async order => {
            try {
                ticker = global.tickers[order.symbol]
                if (!ticker || !order.target) return;

                if (
                        (order.status === 'sell') ||
                        (ticker.close >= order.target && order.status === 'sellat') 
                    ) {                    
                    // decimals = order.stop.toString().split('.')[1].length
                    console.log(`   Target hit: ${order.id} /  ${order.qty}  ${order.symbol} @ ${order.target}`);
                    if (order.stopResp && order.stopResp.orderId) {
                        try {
                            console.log(`       Canceling stop order on exchange:  ${order.stopResp.orderId}`);
                            const cancelStopResp = await binance.cancel(order.symbol, order.stopResp.orderId);
            
                            const updRes = await orders.updateOne({ _id: order._id }, { $set: {
                                cancelStopResp: cancelStopResp,
                            }});
    
                        } catch {
                            console.error(`Error canceling stop order: ${order.id}`)
                        }
        
                    }
                    console.log(`       Market sell:  ${order.id} / ${order.qty} ${order.symbol}`);
                    const sellResp = await binance.marketSell(order.symbol, order.qty);
        
                    const updRes = await orders.updateOne({ _id: order._id }, { $set: {
                        status: "targetsold",
                        sellResp: sellResp
                    }});
                }

            } catch(err) {
                console.error(`ERROR: ${order.id} / ${err.message}`);
                await orders.updateOne({ _id: order._id }, { $set: {
                    status: "err",
                    error: err.message
                }});
            }
        });
    }, 1000);


    // UPDATE position pnl
    setInterval(async () => {
            
        const boughtOrdersCursor = await orders.aggregate([{
            $match: { status: {$in: ['sell', 'sellat']} }
        }]);
        const boughtOrders = await boughtOrdersCursor.toArray();

        console.log(dateFormat())
        boughtOrders.forEach(async order => {
            try {
                ticker = global.tickers[order.symbol]
                if (!ticker || !order.orderResp) return;

                orderResp = order.orderResp;

                const buyCommission = orderResp.fills.reduce( (a,x) => a + x.commission, 0);
                const totalPaid = orderResp.fills.reduce( (a,x) => a + x.qty * x.price, 0);
                const qty = orderResp.fills.reduce( (a,x) => a + x.qty, 0);
                const avgBuyPrice = (totalPaid / qty).toFixed(qtyDecimals[order.symbol]);

                
                const pnl = ((ticker.close - avgBuyPrice) / ticker.close * 100).toFixed(2);

                const updRes = await orders.updateOne({ _id: order._id }, { $set: {
                    qty: amount ,
                    avgBuyPrice,
                    buyResp: orderResp,
                    buyCommission,
                    qty,
                    pnl

                }});

                // const updRes = await orders.updateOne({ _id: order._id }, { $set: {
                //     pnl: ((ticker.close - order.avgBuyPrice) / ticker.close * 100).toFixed(2),
                // }});

        

            } catch(err) {
                console.error(`ERROR: ${order.id} / ${err.message}`);
            }
        });
    }, 1000);


})();


// [
//     {
//         "timeCreated": dateFormat("isoDateTime"),
//         "status": "live",
//         "symbol": "BTCUSDT",
//         "type": "buyAt",
//         "trigger": 20000,
//         "stop": 18000,
//         "target": 30000
//     },
//     {
//         "timeCreated": dateFormat("isoDateTime"),
//         "status": "live",
//         "symbol": "BNBUSDT",
//         "type": "buyAt",
//         "trigger": 20000,
//         "stop": 18000,
//         "target": 30000
//     },
//     {
//         "timeCreated": dateFormat("isoDateTime"),
//         "status": "live",
//         "symbol": "ALGOUSDT",
//         "type": "buyAt",
//         "trigger": 20000,
//         "stop": 18000,
//         "target": 30000
//     },
//     {
//         "timeCreated": dateFormat("isoDateTime"),
//         "status": "live",
//         "symbol": "DOTUSDT",
//         "type": "buyAt",
//         "trigger": 20000,
//         "stop": 18000,
//         "target": 30000
//     }
// ].forEach(async order => {
//     await orders.insertOne({
//         id: `${dateFormat('yymmdd')}-${order.symbol}-${dateFormat('HHMMss')}`,
//         ...order
//     });
// });

// binance.websockets.miniTicker(markets => {
//     console.info(markets);
//     storeData(markets, './markets.json')
// });