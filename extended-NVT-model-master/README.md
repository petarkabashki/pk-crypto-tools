# extended-NVT-model
I have more tests in the framework of NVT

"nvt_data_from_coinmetrics.py" is main funtion, you can directly run the program

The folling artical is my summary:(picture will be a pacage named fig_nvt)

                                                  比特币估值模型——NVT的进一步思考
编者按：本文主要介绍作者对现有比特币估值模型的一些认识，并且就比特币估值大神Willy Woo 提出的NVT指标进行了分析并做出一些新的尝试，得到一些新的结论，最后希望能够结合因果关系的研究不断的深入。

估值模型现状：
目前对数字货币的估值模型层出不穷，各个领域的专家都从自己的领域提出了不同的估值模型，而且绝大多数的人都选择了数字货币鼻祖——比特币作为研究标的。认真思考一下就会发现：如果忽略具体的研究方法，我们可以发现大家都是在做同一件事——发现和度量数字货币真正的utility，本文的主题将聚焦到比特币的估值模型上。
传统金融当中估值模型有：CAPM、DCF（现金流折现法）、比较估值法、随机理论中的一些期权定价模型等，这些模型和方法都有一个很强的假设：一个成熟的金融市场；但是，数字货币市场作为一个新生的去中心化的网路结构有其自身特点，而且在数字货币市场中也不存在公司、现金流的概念；所以，在这样刚刚生长了十年的数字货币市场不能盲目的套用传统领域的估值模型，我们需要结合区块链自身的结构特点以及数字货币的特点去研究。
目前涌现出的一些比较出名的比特币估值模型包括：NVT [1][2]、NVM [3]、LPPLS [4]、PMR [5]、《A bitcoin valuation model assuming equilibrium of miners’ market –based on derivative pricing theory》[6]等；分析这些估值指标和模型以后，我们会发现实际上我们关注到的utility衡量指标无非是：比特币的链上数据交易量、活跃用户数量、以及挖矿成本；此外，由于区块链技术本身的分布式特点，又加入了与网络效应对应的定律——梅特卡夫定律；上面的几个关键词几乎可以涵盖目前所有的估值模型的核心内容。但是这些指标是不是真的可以代表比特币的真正的价值，目前并没有一个确切的结论；此外，目前的很多工作都是在做相关性的研究(研究一些指标与市场走向相关的指标)，因果性的研究才是我们终极目标。有关因果关系研究请参看另一篇研究《走过了相关，就是因果时代》（链接到原文）
目前的估值模型的研究还处于非常初步的阶段，但是每一种方法的尝试都是一种对比特币价值探讨的一个推进过程，非常有必要。本篇文章主要讨论比特币估值大神提出的NVT模型以及做出的一些扩展研究，希望与大家共同探讨。

NVT模型简介：
NVT模型是Willy Woo [1] 提出的判断比特币价格与基本面背离情况的指标，其核心思想来源于传统金融中公司的PE（市盈率）指标，将比特币网络看作一家公司，而将链上数据交易量看作公司的现金流，类比于PE指标NVT（Network Value to Transactions ratio）的构建如下：
NVT=比特币市值/每日链上数据交易量
从表达式我们可以看出：；NVT指标实际上度量了比特币价格相对于真实价值的变化情况，其中用比特币链上交易量数据度量了比特币的真实价值，也就是度量了比特币的utility如果在一定的合理范围之内波动，比特币的变化被认为是合理的，但是低于一定界限和超过一定的界限都是不合理的，过分偏高表现为价格高估（泡沫），过分低则体现为被严重低估。下图为Willy Woo做出的NVT指标：
 
图1
从图中我们可以看出几个问题：
	在2010到2012年之间的NVT指标是一个失效的状态，当时比特币处在一个快速增长的时期，NVT指标并不能客观的反映比特币的增长，所以NVT指标更加适用于发展相对稳定的阶段的行情分析；
	关于合理区间的定义：Willy Woo没有一个标准合理的定义（见下图2），目前相对比较合理的方法：以最大化刻画历史数据中泡沫阶段为目标确定合理边界；
	NVT指标中利用每日交易量去做运算波动率是很大的，Willy Woo选择了28天作为交易量的移动平均作为计算指标的链上交易数据量（28MA(链上数据交易量)）,但是为什么选择28天的数据，其他时间长度的移动平均是不是会有相同的效果？
	NVT指标选择了链上数据交易量作为比特币utility的衡量，但是交易量是否真的能够更好的反应比特币的utility吗？会不会有其他的更好的指标去衡量？如：交易所交易量、活跃地址数量、交易次数、交易量的增量、或者这些指标之间的一些组合指标；
	NVT指标很大程度上没有预测效果，它是基于历史数据计算得到的，最大的效用是对于目前大行情的判断，但是用于计算未来的指标的数据事先是无法得到的；是否能够构造一些有用的指标，与NVT指标相结合可以对行情做出一些分析？

 
图2
NVT扩展研究：
针对以上的一些问题，下面尝试利用不同的数据衡量比特币utility计算NVT指标，并给出一些具体分析：
	Utility：链上数据交易量
 
图3
	Utility：交易所交易量
 
图4
	Utility：链上数据交易量+交易所交易量
 
图5
	Utility：活跃地址数量、（活跃地址数量）2
 
图6
 
图7
	Utility：交易次数
 
图8
	Utility：平均每个活跃地址的交易量=链上数据交易量/活跃地址数量
 
图9
	 Utility：平均每次交易的交易量=链上数据交易量/交易次数
 
图10

结果分析：
	在NVT框架下，我们尝试上面7种方式度量比特币utility，得到的NVT指标如图3~图10。可以得出以下结论：
	利用链上数据交易量去度量比特币的utility得到的NVT指标（图3）在一个范围内波动，没有明显的上涨下跌趋势，如果能够找到合理的变动区间对于当前市场状态（泡沫/低估）的判断是一个相对合适的指标；
	利用交易所交易量去度量比特币的utility得到的NVT指标（图4）有明显的下降趋势，可以看出交易所的交易量包含了更多的投机因素，导致NVT整体的变化幅度明显增大；这种情况下，单纯的考虑一个确定的合理区间，利用NVT指标度量市场情况是不合适的；
	利用链上数据交易量和交易所交易量之和去度量比特币的utility计算得到NVT指标（图5）变化趋势基本与只用交易所数据走势基本相同；所以相比而言，链上交易量更能客观反映比特币的utility；
	利用活跃地址数量以及其平方（结合梅特卡夫定律）度量比特币的utility得到NVT指标（图6、图7）与比特币的走势基本一致，变化幅度比较大，不能作为一个稳定的指标衡量比特币的价格走向；
	利用每日链上交易次数度量比特币的utility得到的NVT指标（图8）与活跃地址数量与非常同质的效果，从图6和图8的对比中可以看出，某种程度上链上的日交易次数与活跃地址数量对于比特币网络来说是一个衡量utility的同质化指标；
	利用平均每个活跃地址链上交易量与平均每次交易的交易量度量比特币utility得到的NVT指标（图9、图10）具有同质化的效果，两个指标整体都呈现上升趋势且走势基本一致；但是与纯粹的活跃地址数量以及交易次数相对变化幅度较小，可见，将链上数据交易量与活跃地址数量、交易次数相结合，可能加入了新的utility信息；
综上分析可以看出，综合考虑链上数据交易量、活跃地址数量和交易次数提供了更多的utility信息，但此时不适合用确定的合理区间去度量NVT指标的合理性为了比较哪个指标对市场有更好的刻画和预测效果，我们利用历史数据判断关键操作点（红线与蓝线交叉点）的准确性以及预测性。
需要说明的是，图11和图12中参数设置完全相同，红色线为NVT指标（蓝线）的前90日均线，从图中可以看出如果以红蓝线交叉点作为交易操作点大部分情况是两张图是相同的；但是就最近的行情，两张图给出了不同的操作指引；进一步分析可以知道，在控制交易量相同作用的情况下，活跃地址数量没有大的上浮，但是交易的频次明显增加；
此外，从一些局部细节上可以看出，utility=(Volume )/(Active address)（图11）时的NVT反应更加敏感，能抓住小的操作机会（如18年波段性下跌的情况），utility=(Volume )/(Transaction counts)（图12）时的NVT反应比较保守；但是二者在大行情下的判断是基本相同的。

结论：
本文作为NVT指标的扩展性研究，从传统金融的PE角度看，PE指标是衡量大众一个公司盈利能力的认可度，应该是在一个水平（一般10%）附近波动是比较合理的；目前交易量、活跃地址、交易频次等单个或者组合作为utility的度量都还不是最好的指标，NVT框架下的我们仍然需要继续探索更加有效的utility度量指标。
此外，关于数字货币的估值模型的研究我们也会持续跟进，也希望能够与因果关系的研究相结合不断深入研究数字货币内在价值的支撑点。









 
图11 Volume/Active address-NVT
 
图12 Volume/Transaction counts-NVT






 






参考文献：

[1] http://charts.woobull.com/bitcoin-nvt-ratio/ 
[2] https://www.norupp.com/willy-woo-interview-the-nvt-ratio-and-future-of-cryptocurrencies/
[3] https://medium.com/cryptolab/network-value-to-metcalfe-nvm-ratio-fd59ca3add76 
[4] https://arxiv.org/abs/1803.05663 
[5] https://medium.com/@clearblocks/valuing-bitcoin-and-ethereum-with-metcalfes-law-aaa743f469f6 
[6] https://usethebitcoin.com/wp-content/uploads/2019/01/A-Bitcoin-Valuation-Model-Assuming-Equilibrium-Of-Miners%E2%80%99-Market-Based-On-Derivative-Pricing-Theory.pdf








