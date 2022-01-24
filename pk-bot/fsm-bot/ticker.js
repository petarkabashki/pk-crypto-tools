
var zmq = require('zeromq')
, publisher = zmq.socket('pub');


const Binance = require('binance-api-node').default

const binanceClient = Binance({
    apiKey: process.env.BINANCE_API_KEY,
    apiSecret:  process.env.BINANCE_API_SECRET,
  //   getTime: xxx,
})

global.tickers = {}

publisher.bindSync("tcp://*:5556");
publisher.bindSync("ipc://ticker.ipc");

binanceClient.ws.allTickers(tickers => {
    global.tickers['binance'] = tickers;
})

// KUCOIN
// const Kucoin_API = require('kucoin-node-sdk');
// Kucoin_API.init(require('./kucoin-api.config'));

// const datafeed = new Kucoin_API.websocket.Datafeed();

// // close callback
// datafeed.onClose(() => {
//   console.log('kucoin ws closed, status ', datafeed.trustConnected);
// });

// // connect
// datafeed.connectSocket();

// // subscribe
// const topic = `/ALTS/ticker:all`;
// const callbackId = datafeed.subscribe(topic, (message) => {
// //   if (message.topic === topic) {
//     console.log(message.data);
// //   }
// });

// console.log(`kucoin subscribe id: ${callbackId}`);
// setTimeout(() => {
//   // unsubscribe
//   datafeed.unsubscribe(topic, callbackId);
//   console.log(`kucoin unsubscribed: ${topic} ${callbackId}`);  
// }, 5000);

// const main = async () => {
//     const getTimestampRl = await Kucoin_API.rest.Others.getTimestamp();
//     console.log(getTimestampRl.data);
// };

// main();

// var WebSocketClient = require('websocket').client;

// var kucoinClient = new WebSocketClient();
// kucoinClient.on('connectFailed', function(error) {
//     console.log('Connect Error: ' + error.toString());
// });

// client.on('connect', function(connection) {
//     console.log('WebSocket Client Connected');
//     connection.on('error', function(error) {
//         console.log("Connection Error: " + error.toString());
//     });
//     connection.on('close', function() {
//         console.log('echo-protocol Connection Closed');
//     });
//     connection.on('message', function(message) {
//         if (message.type === 'utf8') {
//             console.log("Received: '" + message.utf8Data + "'");
//         }
//     });
    
//     function sendNumber() {
//         if (connection.connected) {
//             var number = Math.round(Math.random() * 0xFFFFFF);
//             connection.sendUTF(number.toString());
//             setTimeout(sendNumber, 1000);
//         }
//     }
//     sendNumber();
// });

// client.connect('ws://localhost:8080/market/ticker:all', 'echo-protocol');

// const Kucoin = require("kucoin-websocket-api")

// const kucoinClient = new Kucoin()
// const kucoinApi = require('kucoin-node-api');

// kucoinApi.init({topic: "ticker", symbols: ['all']}, (msg) => {
//     let data = JSON.parse(msg)
//     console.log(data)
// })

// kucoinApi.ws.allTickers(tickers => {
//     // global.tickers['binance'] = tickers;
//     console.log(tickers)
// })

setInterval(() => {
    if(!global.tickers) { return; }

    for (const [exchange, tickers] of Object.entries(global.tickers)) {
        // console.log(key, value);

        tickers.forEach(ticker => {
            // console.log(`TICKER ${exchange} ${ticker.symbol}`)
            publisher.send(`TICKER ${exchange} ${ticker.symbol} ${JSON.stringify(ticker)}`);
        });
    }
    
},1000)
// while (true) {
// // Get values that will fool the boss
// var zipcode     = rand(100000)
//   , temperature = rand(215, -80)
//   , relhumidity = rand(50, 10)
//   , update      = `${zeropad(zipcode)} ${temperature} ${relhumidity}`;
// publisher.send(update);
// }