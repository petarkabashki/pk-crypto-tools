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

    positionSize = 100;

    // liveOrders = await orders.find({"status": "live"})
    // let liveOrdersRes = await orders.aggregate([{
    //     $match: { status: "live" }
    // }])

    binance.websockets.miniTicker(tickers => { global.tickers = { ...global.tickers, ...tickers }; });


    setInterval(async () => {

        const liveOrdersCursor = await orders.aggregate([{
            $match: { type: "buyBelow", status: "live" }
        }]);
        const liveOrders = await liveOrdersCursor.toArray();

        console.log(dateFormat())
        liveOrders.forEach(async order => {
            ticker = global.tickers[order.symbol]
            if (!ticker) return;

            if (ticker.close <= order.trigger) {
                // console.log(`${order.symbol}`)
                const amount = Math.floor(positionSize / ticker.close);
                console.log(`   Buying: ${order.id} / ${amount}  ${order.symbol} @ ${ticker.close}`);
                orderResp = await binance.marketBuy(order.symbol, amount);

                const updRes = await orders.updateOne({ _id: order._id }, { $set: {
                    status: "bought",
                    buyResp: orderResp
                }});
            }
        });
    }, 2000);

    setInterval(async () => {

        const boughtOrdersCursor = await orders.aggregate([{
            $match: { type: "buyBelow", status: "bought" }
        }]);
        const boughtOrders = await boughtOrdersCursor.toArray();

        console.log(dateFormat())
        boughtOrders.forEach(async order => {
            
            amount = Number(order.buyResp.executedQty);
            // decimals = order.stop.toString().split('.')[1].length
            console.log(`   Setting stop: ${order.id} /  ${amount}  ${order.symbol} @ ${order.stop}`);
            orderResp = await binance.sell(order.symbol, amount, 
                (order.stop * 0.99).toFixed(order.stop.toString().split('.')[1].length), 
                {stopPrice: order.stop, type: "STOP_LOSS_LIMIT"});

            const updRes = await orders.updateOne({ _id: order._id }, { $set: {
                status: "stopset",
                stopResp: orderResp
            }});
        
        });
    }, 2000);


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