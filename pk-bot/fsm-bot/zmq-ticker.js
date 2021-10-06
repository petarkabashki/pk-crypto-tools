
var zmq = require('zeromq')
, publisher = zmq.socket('pub');


const Binance = require('binance-api-node').default

const client = Binance({
    apiKey: process.env.BINANCE_API_KEY,
    apiSecret:  process.env.BINANCE_API_SECRET,
  //   getTime: xxx,
})


publisher.bindSync("tcp://*:5556");
publisher.bindSync("ipc://ticker.ipc");

client.ws.allTickers(tickers => {
    global.tickers = tickers;
})

setInterval(() => {
    if(!global.tickers) { return; }

    global.tickers.forEach(ticker => {
        // console.log(ticker)
        publisher.send(`TICKER ${ticker.symbol} ${JSON.stringify(ticker)}`);
    });
},1000)
// while (true) {
// // Get values that will fool the boss
// var zipcode     = rand(100000)
//   , temperature = rand(215, -80)
//   , relhumidity = rand(50, 10)
//   , update      = `${zeropad(zipcode)} ${temperature} ${relhumidity}`;
// publisher.send(update);
// }