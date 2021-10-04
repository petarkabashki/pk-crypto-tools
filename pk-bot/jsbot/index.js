require('dotenv').config();
const fs = require('fs')
const { MongoClient } = require("mongodb");


const Binance = require('binance-api-node').default


const storeData = (data, path) => {
    try {
        fs.writeFileSync(path, JSON.stringify(data))
    } catch (err) {
        console.error(err)
    }
}
const loadData = (path) => {
    try {
        return fs.readFileSync(path, 'utf8')
    } catch (err) {
        console.error(err)
        return false
    }
}

const xchClient = Binance({
  apiKey: process.env.BINANCE_API_KEY,
  apiSecret:  process.env.BINANCE_API_SECRET,
//   getTime: xxx,
})

// global.dbSymbols = [];
global.tickers = {};

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));


(async () => {

    global.xchInfo = await xchClient.exchangeInfo();
    global.xchSymbols = Object.fromEntries(global.xchInfo.symbols.map(s => [s.symbol, {...s, ...{filters: Object.fromEntries(s.filters.map(f => [f.filterType, f])) }}]));
    // console.log(xchInfo);
    // storeData(global.xchInfo, './binance-exchangeInfo.json');

    // xchSymbols = Object.fromEntries(exchinfo.symbols.map(s => [s.symbol, s]))



    // const dateFormat = require('dateformat')
    const dateFormatModule = await import('dateformat')
    const dateFormat = dateFormatModule.default;


    // dateFormat(new Date(), "yyyy-mm-dd h:MM:ss");




    const uri = "mongodb://localhost:27017";
    const mongoClient = new MongoClient(uri);

    await mongoClient.connect();
    db = mongoClient.db('jsbot');
    orders = db.collection('orders')

    const symbols = await orders.distinct('symbol');
    // const dbSymbolsCursor = await orders.aggregate([
    //     {
    //         $group: {
    //             _id: null,
    //             symbols: {
    //               $push: '$symbol'
    //             }
    //           }
    //     }
    // ]);

    // if(await dbSymbolsCursor.hasNext()) {
    //     global.dbSymbols = (await dbSymbolsCursor.next()).symbols;
    //     console.log(global.dbSymbols);
    // }

    // dbSymbolsCursor.close()

    xchClient.ws.miniTicker(symbols, ticker => {
        global.tickers[ticker.symbol] = ticker;
    })

    truncQty = (symbol, qty) => {
        const symbolInfo = global.xchSymbols[symbol];
        const stepSize = Number(symbolInfo.filters['LOT_SIZE'].stepSize);
        return (Math.floor(Number(qty) / stepSize) * stepSize).toFixed(symbolInfo.baseAssetPrecision);
    } 

    
    function calcAvgPrice(order) {
        const ticker = global.tickers[order.symbol];
        const orderResp = order.buyResp;
        const buyCommission = orderResp.fills.reduce( (a,x) => a + Number(x.commission), 0.0);
        const totalPaid = orderResp.fills.reduce( (a,x) => a + Number(x.qty) * Number(x.price), 0);
        // const qty = orderResp.fills.reduce( (a,x) => a + Number(x.qty), 0.0);
        const netQty = (Number(order.qty) - Number(buyCommission));
        const avgBuyPrice = (totalPaid / Number(order.qty));
        const netAvgBuyPrice = (totalPaid / netQty);
        const posPnl = (ticker.curDayClose - avgBuyPrice) * Number(order.qty);
        const posPnlPercent = ((ticker.curDayClose - avgBuyPrice) / avgBuyPrice * 100).toFixed(4);

        return {
            netQty,
            netAvgBuyPrice,
            avgBuyPrice,
            buyCommission,
            posPnl,
            posPnlPercent
        };
    }

// BUY IF PRICE BELOW TRIGGER
    setInterval(async () => {

        const liveOrdersCursor = await orders.aggregate([{
            $match: { status: { $in: ['buy', 'buyat'] } }
        }]);
        const liveOrders = await liveOrdersCursor.toArray();

        console.log(dateFormat(), 'Checking buy levels...')
        liveOrders.forEach(async order => {
            try {
                ticker = global.tickers[order.symbol]
                if (!ticker) return;
    
                if (
                        (order.status === 'buy')  ||
                        (order.status == 'buyat' && ticker.curDayClose <= order.trigger)
                    
                    ) {                    
                        const amount = truncQty(order.symbol, order.qty || (order.size / ticker.curDayClose)); 
                        console.log(`   Buying: ${order.id} /  ${amount})  ${order.symbol} @ ${ticker.curDayClose}`);
                        const buyResp = await xchClient.order({
                        symbol: order.symbol,
                        side: 'BUY',
                        type: 'MARKET',
                        quantity: amount
                        });

                        const updRes = await orders.updateOne({ _id: order._id }, { $set: {
                            status: "sellat",
                            action: "setstop",
                            buyResp: buyResp,
                            qty: truncQty(order.symbol, buyResp.executedQty * 0.999)
                            // ...calcNetQty(orderResp)
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
            $match: { action: "setstop" }
        }]);
        const boughtOrders = await boughtOrdersCursor.toArray();

        console.log(dateFormat(), 'Setting stops...')
        boughtOrders.forEach(async order => {
            try {
                // decimals = order.trigger.toString().split('.')[1].length

                if (order.stopResp && order.stopResp.orderId) { 
                    try {
                        console.log(`   Canceling previous stop order :  ${order.stopResp.orderId}`);
                        const cancelStopResp = await xchClient.cancelOrder({ symbol: order.symbol, orderId: order.stopResp.orderId });        
                        const updRes = await orders.updateOne({ _id: order._id }, { $set: {
                            cancelStopResp: cancelStopResp,
                        }});        
                    } catch {
                        console.error(`Error canceling stop order: ${order.id}`)
                    }
                }

                console.log(`   Setting stop: ${order.id} /  ${order.buyResp.executedQty})  ${order.symbol} @ ${order.stop}`);
                orderResp = await xchClient.order({
                    symbol: order.symbol,
                    side: 'SELL',
                    type: 'STOP_LOSS_LIMIT',
                    price: order.stop,
                    stopPrice: order.stop,
                    quantity: order.qty
                  });

                const updRes = await orders.updateOne({ _id: order._id }, { $set: {
                    // status: "sellat",
                    action: "",
                    stopResp: orderResp
                }});
            } catch(err) {
                console.error(`ERROR: ${order.id} / ${err.message}`);
                await orders.updateOne({ _id: order._id }, { $set: {
                    // status: "err",
                    error: err.message
                }});
            }
        
        });
    }, 3000);

// SELL
    setInterval(async () => {
        
        const boughtOrdersCursor = await orders.aggregate([{
            $match: { status: {$in: ['sell', 'sellat']} }
        }]);
        const boughtOrders = await boughtOrdersCursor.toArray();

        console.log(dateFormat(), 'Checking sell targets...')
        boughtOrders.forEach(async order => {
            try {
                ticker = global.tickers[order.symbol]
                if (!ticker || !order.target) return;

                if (
                        (order.status === 'sell') ||
                        (ticker.curDayClose >= order.target && order.status === 'sellat') 
                    ) {

                    // console.log(`   Target hit: ${order.id} /  ${order.qty}  ${order.symbol} @ ${order.target}`);
                    if (order.stopResp && order.stopResp.orderId) {
                        try {
                            console.log(`   Canceling stop order on exchange:  ${order.stopResp.orderId}`);                            
                            const cancelStopResp = await xchClient.cancelOrder({ symbol: order.symbol, orderId: order.stopResp.orderId });            
                            const updRes = await orders.updateOne({ _id: order._id }, { $set: {
                                cancelStopResp: cancelStopResp,
                            }});
    
                        } catch {
                            console.error(`Error canceling stop order: ${order.id}`);
                        }        
                    }
                    console.log(`   Market sell:  ${order.id} / ${order.qty} ${order.symbol} @ ${ticker.curDayClose}`);
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
    }, 3000);

    // UPDATE position avg price & pnl
    setInterval(async () => {
            
        const boughtOrdersCursor = await orders.find({
            buyResp: { $exists : true },
            qty: { $exists: true},
            status: {$in: ['sell', 'sellat']} 
        });
        const boughtOrders = await boughtOrdersCursor.toArray();

        console.log(dateFormat(), 'Calculate Avg price and PNL');
        boughtOrders.forEach(async order => {
            try {
                // ticker = global.tickers[order.symbol]
                // if (!ticker || !order.orderResp) return;

                const updRes = await orders.updateOne({ _id: order._id }, { $set: {
                    ...calcAvgPrice(order)
                }});
            } catch(err) {
                console.error(`ERROR: ${order.id} / ${err.message}`);
            }
        });
    }, 5000);

    // UPDATE stop losses
    setInterval(async () => {
        
        const dbOrdersCursor = await orders.aggregate([{
            $match: { status: {$in: ['sell', 'sellat']} }
        }]);
        const dbOrders = await dbOrdersCursor.toArray();

        console.log(dateFormat(), "Updating stops in db...")
        dbOrders.forEach(async order => {
            try {
                ticker = global.tickers[order.symbol]
                if (!ticker > !order.stopResp) return;

                stopOrderResp = await xchClient.getOrder({
                    symbol: order.symbol,
                    orderId: order.stopResp.orderId,
                  });

                if(stopOrderResp.status ==='FILLED') {
                    const updRes = await orders.updateOne({ _id: order._id }, { $set: {
                        status: "stopped",
                        stopOrderResp: stopOrderResp
                    }});
                
                }

            } catch(err) {
                console.error(`ERROR updating stop order in db: ${order.id} / ${err.message}`);
                await orders.updateOne({ _id: order._id }, { $set: {
                    // status: "err",
                    error: err.message
                }});
            }
        });
    }, 3000);


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