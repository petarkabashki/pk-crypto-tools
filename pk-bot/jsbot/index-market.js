
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

const client = Binance({
  apiKey: process.env.BINANCE_API_KEY,
  apiSecret:  process.env.BINANCE_API_SECRET,
//   getTime: xxx,
})

// global.dbSymbols = [];
global.tickers = {};

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));


(async () => {

    global.exchangeInfo = await client.exchangeInfo();
    global.exchangeSymbols = Object.fromEntries(global.exchangeInfo.symbols.map(s => [s.symbol, {...s, ...{filters: Object.fromEntries(s.filters.map(f => [f.filterType, f])) }}]));
    // console.log(exchangeInfo);
    // storeData(global.exchangeInfo, './binance-exchangeInfo.json');

    // exchangeSymbols = Object.fromEntries(eexchangeInfo.symbols.map(s => [s.symbol, s]))



    // const dateFormat = require('dateformat')
    const dateFormatModule = await import('dateformat')
    const dateFormat = dateFormatModule.default;


    // dateFormat(new Date(), "yyyy-mm-dd h:MM:ss");




    const uri = "mongodb://localhost:27017";
    const mongoClient = new MongoClient(uri);

    await mongoClient.connect();
    db = mongoClient.db('jsbot');
    dbOrders = db.collection('orders')

    // const dbSymbols = await dbOrders.distinct('symbol');
    // const dbSymbolsCursor = await dbOrders.aggregate([
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

    // client.ws.miniTicker(symbols, ticker => {
    //     global.tickers[ticker.symbol] = ticker;
    // })

    client.ws.allTickers(tickers => {
        global.tickers = Object.fromEntries(tickers.map(t => [t.symbol, t]));
    })


    truncQty = (symbol, qty) => {
        const symbolInfo = global.exchangeSymbols[symbol];
        // console.log('symbolInfo', global.exchangeSymbols)
        const stepSize = Number(symbolInfo.filters['LOT_SIZE'].stepSize);
        return (Math.floor(Number(qty) / stepSize) * stepSize).toFixed(symbolInfo.baseAssetPrecision);
    } 

    

// BUY IF PRICE BELOW TRIGGER
    setInterval(async () => {

        const buyDbOrdersCursor = await dbOrders.find({ status: { $in: ['buy', 'buyat'] } });
        const buyDbOrders = await buyDbOrdersCursor.toArray();

        console.log(dateFormat(), 'Checking buy levels...');
        buyDbOrders.forEach(async dbOrder => {
            try {
                ticker = global.tickers[dbOrder.symbol]
                console.log(`   CHECKING: ${dbOrder.id} /  ${dbOrder.size})  ${dbOrder.symbol} @ ${ticker.curDayClose}`);
                if (!ticker) {
                    console.log(`TICKER NOT FOUND: ${symbol}`);
                    return;
                }
                if (
                        (dbOrder.status === 'buy')  ||
                        (dbOrder.status == 'buyat' && ticker.curDayClose <= dbOrder.trigger)
                    
                    ) {                    
                        const amount = truncQty(dbOrder.symbol, dbOrder.qty || (dbOrder.size / ticker.curDayClose)); 
                        console.log(`   Buying: ${dbOrder.id} /  ${amount})  ${dbOrder.symbol} @ ${ticker.curDayClose}`);
                        const buyResp = await client.order({
                            symbol: dbOrder.symbol,
                            side: 'BUY',
                            type: 'MARKET',
                            quantity: amount
                        });

                        const baseAssetFreeBalance = (await client.accountInfo()).balances
                            .find(b => b.asset === global.exchangeSymbols[dbOrder.symbol].baseAsset)
                            .free;
                        const qty = truncQty(dbOrder.symbol, Math.min(Number(buyResp.executedQty) * 0.999, baseAssetFreeBalance));

                        console.log('baseAssetFreeBalance', baseAssetFreeBalance)
                        console.log('qty', qty)

                        stopResp = await client.order({
                            symbol: dbOrder.symbol,
                            side: 'SELL',
                            type: 'STOP_LOSS_LIMIT',
                            price: dbOrder.stop,
                            stopPrice: dbOrder.stop,
                            quantity: qty
                          });

                        const updRes = await dbOrders.updateOne({ _id: dbOrder._id }, { $set: {
                            status: "sellat",
                            action: "",
                            qty,
                            buyResp,
                            stopResp
                        }});
                }
            } catch(err) {
                console.error(`ERROR: ${dbOrder.id} / ${err.message}`);
                await dbOrders.updateOne({ _id: dbOrder._id }, { $set: {
                    status: "err",
                    error: err.message
                }});
            }
        });
    }, 1000);

// SET STOPLOSS    
    setInterval(async () => {

        const dbOrdersCursor = await dbOrders.find({ action: "setstop" });
        console.log(dateFormat(), 'Setting stops...')
        dbOrdersCursor.forEach(async dbOrder => {
            try {
                if (dbOrder.stopResp && dbOrder.stopResp.dbOrderId) { 
                    try {
                        console.log(`   Canceling previous stop dbOrder :  ${dbOrder.stopResp.dbOrderId}`);
                        const cancelStopResp = await client.cancelOrder({ symbol: dbOrder.symbol, dbOrderId: dbOrder.stopResp.dbOrderId });        
                        const updRes = await dbOrders.updateOne({ _id: dbOrder._id }, { $set: {
                            cancelStopResp: cancelStopResp,
                        }});        
                    } catch {
                        console.error(`Error canceling stop dbOrder: ${dbOrder.id}`)
                    }
                }


                console.log(`   Setting stop: ${dbOrder.id} /  ${dbOrder.qty})  ${dbOrder.symbol} @ ${dbOrder.stop}`);
                dbOrderResp = await client.order({
                    symbol: dbOrder.symbol,
                    side: 'SELL',
                    type: 'STOP_LOSS_LIMIT',
                    price: dbOrder.stop,
                    stopPrice: dbOrder.stop,
                    quantity: dbOrder.qty
                  });

                const updRes = await dbOrders.updateOne({ _id: dbOrder._id }, { $set: {
                    action: "",
                    stopResp: dbOrderResp
                }});
            } catch(err) {
                console.error(`ERROR: ${dbOrder.id} / ${err.message}`);
                await dbOrders.updateOne({ _id: dbOrder._id }, { $set: {
                    error: err.message
                }});
            }
        
        });
    }, 3000);

// SELL
    setInterval(async () => {
        const sellDbOrdersCursor = await dbOrders.find({ status: {$in: ['sell', 'sellat']}});
        console.log(dateFormat(), 'Checking sell targets...')
        sellDbOrdersCursor.forEach(async dbOrder => {
            try {
                ticker = global.tickers[dbOrder.symbol]
                if (!ticker || !dbOrder.target) return;

                if (
                        (dbOrder.status === 'sell') ||
                        (ticker.curDayClose >= dbOrder.target && dbOrder.status === 'sellat') 
                    ) {

                    console.log(`   Sell order: ${dbOrder.id} /  ${dbOrder.qty}  ${dbOrder.symbol} @ ${dbOrder.target}`);
                    if (dbOrder.stopResp && dbOrder.stopResp.orderId) {
                        try {
                            console.log(`   Canceling stop dbOrder on exchange:  ${dbOrder.stopResp.orderId}`);                            
                            const cancelStopResp = await client.cancelOrder({ symbol: dbOrder.symbol, orderId: dbOrder.stopResp.orderId });            
                            const updRes = await dbOrders.updateOne({ _id: dbOrder._id }, { $set: {
                                cancelStopResp: cancelStopResp,
                            }});
    
                        } catch {
                            console.error(`Error canceling stop dbOrder: ${dbOrder.id}`);
                        }        
                    }
                    console.log(`   Market sell:  ${dbOrder.id} / ${dbOrder.qty} ${dbOrder.symbol} @ ${ticker.curDayClose}`);
                    const sellResp = await client.order({
                        symbol: dbOrder.symbol,
                        side: 'SELL',
                        type: 'MARKET',
                        quantity: dbOrder.qty
                      });
        
                    const updRes = await dbOrders.updateOne({ _id: dbOrder._id }, { $set: {
                        status: "sold",
                        sellResp: sellResp
                    }});
                }

            } catch(err) {
                console.error(`ERROR: ${dbOrder.id} / ${err.message}`);
                await dbOrders.updateOne({ _id: dbOrder._id }, { $set: {
                    status: "err",
                    error: err.message
                }});
            }
        });
    }, 3000);

    // // UPDATE position avg price & pnl
    // setInterval(async () => {
            
    //     const boughtOrdersCursor = await dbOrders.find({
    //         buyResp: { $exists : true },
    //         qty: { $exists: true},
    //         status: {$in: ['sell', 'sellat']} 
    //     });
    //     const boughtOrders = await boughtOrdersCursor.toArray();

    //     console.log(dateFormat(), 'Calculate Avg price and PNL');
    //     boughtOrders.forEach(async dbOrder => {
    //         try {
    //             // ticker = global.tickers[dbOrder.symbol]
    //             // if (!ticker || !dbOrder.dbOrderResp) return;

    //             const updRes = await dbOrders.updateOne({ _id: dbOrder._id }, { $set: {
    //                 ...calcAvgPrice(dbOrder)
    //             }});
    //         } catch(err) {
    //             console.error(`ERROR: ${dbOrder.id} / ${err.message}`);
    //         }
    //     });
    // }, 5000);

    // // UPDATE stop losses
    // setInterval(async () => {
        
    //     const dbOrdersCursor = await dbOrders.aggregate([{
    //         $match: { status: {$in: ['sell', 'sellat']} }
    //     }]);
    //     const dbOrders = await dbOrdersCursor.toArray();

    //     console.log(dateFormat(), "Updating stops in db...")
    //     dbOrders.forEach(async dbOrder => {
    //         try {
    //             ticker = global.tickers[dbOrder.symbol]
    //             if (!ticker > !dbOrder.stopResp) return;

    //             stopOrderResp = await client.getOrder({
    //                 symbol: dbOrder.symbol,
    //                 dbOrderId: dbOrder.stopResp.dbOrderId,
    //               });

    //             if(stopOrderResp.status ==='FILLED') {
    //                 const updRes = await dbOrders.updateOne({ _id: dbOrder._id }, { $set: {
    //                     status: "stopped",
    //                     stopOrderResp: stopOrderResp
    //                 }});
                
    //             }

    //         } catch(err) {
    //             console.error(`ERROR updating stop dbOrder in db: ${dbOrder.id} / ${err.message}`);
    //             await dbOrders.updateOne({ _id: dbOrder._id }, { $set: {
    //                 // status: "err",
    //                 error: err.message
    //             }});
    //         }
    //     });
    // }, 3000);


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
// ].forEach(async dbOrder => {
//     await dbOrders.insertOne({
//         id: `${dateFormat('yymmdd')}-${dbOrder.symbol}-${dateFormat('HHMMss')}`,
//         ...dbOrder
//     });
// });

// binance.websockets.miniTicker(markets => {
//     console.info(markets);
//     storeData(markets, './markets.json')
// });