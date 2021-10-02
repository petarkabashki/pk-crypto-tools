require('dotenv').config();
const fs = require('fs')
const { MongoClient } = require("mongodb");


const Binance = require('binance-api-node').default

const xchClient = Binance({
  apiKey: process.env.BINANCE_API_KEY,
  apiSecret:  process.env.BINANCE_API_SECRET,
//   getTime: xxx,
})

global.dbSymbols = [];
global.tickers = {};

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

// function roundit(x, decimals) {
//     z = Math.pow(10, decimals);
//     return 
// }
const qtyDecimals = {
    'ATOMUSDT' : 2,
    'LUNAUSDT' : 2,
    'EGLDUSDT': 2
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
    const mongoClient = new MongoClient(uri);

    await mongoClient.connect();
    db = mongoClient.db('jsbot');
    orders = db.collection('orders')

    const dbSymbolsCursor = await orders.aggregate([
        {
            $group: {
                _id: null,
                symbols: {
                  $push: '$symbol'
                }
              }
        }
    ]);

    if(await dbSymbolsCursor.hasNext()) {
        global.dbSymbols = (await dbSymbolsCursor.next()).symbols;
        console.log(global.dbSymbols);
    }

    dbSymbolsCursor.close()

    xchClient.ws.miniTicker(global.dbSymbols, ticker => {
        global.tickers[ticker.symbol] = ticker;
    })
  

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
                        (order.status == 'buyat' && ticker.curDayClose <= order.trigger)
                    
                    ) {                    const amount = order.qty || (Number(order.size) / ticker.curDayClose).toFixed(qtyDecimals[order.symbol]); 
                      const orderResp = await xchClient.order({
                        symbol: order.symbol,
                        side: 'BUY',
                        type: 'MARKET',
                        quantity: amount
                      });

                    const buyCommission = orderResp.fills.reduce( (a,x) => a + Number(x.commission), 0);
                    const totalPaid = orderResp.fills.reduce( (a,x) => a + Number(x.qty) * x.price, 0);
                    const qty = orderResp.fills.reduce( (a,x) => a + Number(x.qty), 0);
                    const avgBuyPrice = (totalPaid / qty).toFixed(qtyDecimals[order.symbol])

                    const updRes = await orders.updateOne({ _id: order._id }, { $set: {
                        status: "setstop",
                        qty,
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
                        const cancelStopResp = await xchClient.cancelOrder({ symbol: order.symbol, orderId: order.stopResp.orderId });        
                        const updRes = await orders.updateOne({ _id: order._id }, { $set: {
                            cancelStopResp: cancelStopResp,
                        }});        
                    } catch {
                        console.error(`Error canceling stop order: ${order.id}`)
                    }
                }

                console.log(`   Setting stop: ${order.id} /  ${order.qty}  ${order.symbol} @ ${order.stop}`);
                orderResp = await xchClient.order({
                    symbol: order.symbol,
                    side: 'SELL',
                    type: 'STOP_LOSS_LIMIT',
                    price: (order.stop * 0.99).toFixed(decimals),
                    stopPrice: order.stop,
                    quantity: order.qty
                  });

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
                        (ticker.curDayClose >= order.target && order.status === 'sellat') 
                    ) {

                    console.log(`   Target hit: ${order.id} /  ${order.qty}  ${order.symbol} @ ${order.target}`);
                    if (order.stopResp && order.stopResp.orderId) {
                        try {
                            console.log(`       Canceling stop order on exchange:  ${order.stopResp.orderId}`);                            
                            const cancelStopResp = await xchClient.cancelOrder({ symbol: order.symbol, orderId: order.stopResp.orderId });            
                            const updRes = await orders.updateOne({ _id: order._id }, { $set: {
                                cancelStopResp: cancelStopResp,
                            }});
    
                        } catch {
                            console.error(`Error canceling stop order: ${order.id}`);
                        }        
                    }
                    console.log(`       Market sell:  ${order.id} / ${order.qty} ${order.symbol}`);
                    const sellResp = await xchClient.order({
                        symbol: order.symbol,
                        side: 'SELL',
                        type: 'MARKET',
                        quantity: order.qty
                      });
        
                    const updRes = await orders.updateOne({ _id: order._id }, { $set: {
                        status: "sold",
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
            $match: { status: {$in: ['sell', 'sellat', 'sold']} }
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
                    avgBuyPrice,
                    buyResp: orderResp,
                    buyCommission,
                    qty,
                    pnl

                }});
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