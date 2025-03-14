//+------------------------------------------------------------------+
//|                                                          rsi.mq4 |
//|                                  Copyright 2024, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict
#property script_show_inputs
//--- input parameters
input int      Input1;
input int      Input2;
input int      Input3;
input int      Input4;
input int      Input5;
input int      Input6;
//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
/**
06布林带突破和 RSI 交易系统 V2.0
   复盘1.0， 加入移动止损，收益可以增加跟多。 TODO

06布林带突破和 RSI 交易系统 V1.0
> ## 多头开单
	当RSI大于70，并且是上涨状态。（结果bar判断）
	行情打穿boll 上轨（过程bar进场）
	进场做多。
> ## 空头开单
	当 RSI小于30 ，并且是下跌状态（结果bar判断）
	行情打穿boll 下轨（过程bar进场）
	进场做空。
**/

extern double Lots    = 0.1; //每单的交易量
extern int Slippage   = 2;//最大允许滑点数
extern int    MagicNum;    //自定义订单号
extern int slPoint = 100;
extern int tpPoint = 1000;
static bool done=false;
static double vpoint;
static double minstoplevel;
static int RecordTime;


bool recordTimeOpenFlag = false;
//是否允许多头开仓
bool openLongFlag = false;
//是否允许开空头仓
bool openShortFlag = false;

double spread;//价差
int buynum,sellnum;
double buylots,sellots,buylots1,sellots1,buyprof,sellprof,allprof,buyavg,sellavg,blstop,slstop;
datetime  timeme1=0,timemm1=0;
datetime  timeme2=0,timemm2=0;
int    bTicket_B,STicket_S;

extern  int        pointLimit = 50;
extern   bool    AllowOpen  = true;

int init()//初始化变量
{
   vpoint  = MarketInfo(Symbol(),MODE_POINT);
   minstoplevel  = MarketInfo(Symbol(),MODE_STOPLEVEL);
   Print("minstoplevel=",minstoplevel,"点");
   Print("MODE_POINT=",vpoint,"点");
   return (0);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick(){
   

    //1、价差检查
    checkSpread();
    //2、交易统计
    CountTrades();
   //平仓 
   if(buynum>0)
      CloseOrders1(OP_BUY);
   if(sellnum>0)
      CloseOrders2(OP_SELL);

   if(Time[0]!=RecordTime){
      RecordTime=Time[0];
   }else{
      return;
   }
   double rsi1 =  iRSI(NULL,0,11,PRICE_CLOSE,1);
   double rsi0 =  iRSI(NULL,0,11,PRICE_CLOSE,0);
   
   double bandsUpper0 = iBands(NULL,0,20,2,0,PRICE_CLOSE,MODE_UPPER,0);
   double bandsLower0 = iBands(NULL,0,20,2,0,PRICE_CLOSE,MODE_LOWER,0);
   
   double bandsUpper1 = iBands(NULL,0,20,2,0,PRICE_CLOSE,MODE_UPPER,1);
   double bandsMain1 = iBands(NULL,0,20,2,0,PRICE_CLOSE,MODE_MAIN,1);
   double bandsLower1 = iBands(NULL,0,20,2,0,PRICE_CLOSE,MODE_LOWER,1);
   //double maxPoint=MathMax(MarketInfo(Symbol(),MODE_STOPLEVEL),slPoint)+20;
   //Print("Time ",TimeCurrent()," Ask ",Ask," Bid ",Bid," Open ",Open[0]," High ",High[0]," Low ",Low[0]," Close ",Close[0]," TimeBar ",Time[0]);
   //Print("rsi1 ",rsi1," Close[1] ",Close[1]," Open[1] ",Open[1]," Ask ",Ask," Bid ",Bid," bandsUpper0 ",bandsUpper0," bandsLower0 ",bandsLower0);

   // rsi 小于 70 ， 下跌形态（需要增加）  ，  切当前价格大于 上轨
   if(buynum ==  0 && rsi1 > 70&& Close[1] > Open[1] && Ask > bandsUpper0){
      //double stop_price=Low[1]-slPoint * Point;
      //if (stop_price-Ask>-minstoplevel*Point){
      //   OrderSend(Symbol(), OP_BUY, Lots, Ask, Slippage,Low[1]-slPoint * Point ,0, "Order Buy",  MagicNum, 0, Blue);
      //}
         
      OrderSend(Symbol(), OP_BUY, Lots, Ask, Slippage,Ask-slPoint * Point ,0, "Order Buy",  MagicNum, 0, Blue);
   }
   // rsi 小于 30 ， 上升形态（需要增加） ， 当前价格 打穿下轨
   if(sellnum == 0 && rsi1 < 30&& Open[1] > Close[1] && Bid < bandsLower0){
//      double stop_price=High[1] - slPoint * Point;
//   
//      if (stop_price-Bid > minstoplevel * Point){
//         OrderSend(Symbol(), OP_SELL, Lots, Bid, Slippage,High[1] - slPoint * Point ,0, "Order Sell",  MagicNum, 0, Red);    
//      }
      OrderSend(Symbol(), OP_SELL, Lots, Bid, Slippage,Bid + slPoint * Point ,0, "Order Sell",  MagicNum, 0, Red);
      
      
   }
  


}


//===============================================================
//统计交易
int CountTrades()
  {
   buynum=0;//多单数量
   sellnum=0;//空单数量
   buylots=0;//多单总手数（累加）
   sellots=0;//空单总手数（累加）
   buylots1=0;//多单手数（一单）
   sellots1=0;//空单手数（一单）
   buyprof=0;//多单盈亏（收益+隔夜利息+手续费）
   sellprof=0;//空单盈亏（收益+隔夜利息+手续费）
   buyavg=0;//多单盈亏平衡点。
   sellavg=0;//空单盈亏平衡点
   blstop=0;//多单开单价
   slstop=0;//空单开单价
   bTicket_B=0;//多单ticket
   STicket_S=0;//空单ticket
   for(int cpt=0; cpt<OrdersTotal(); cpt++)
     {
      if(OrderSelect(cpt, SELECT_BY_POS, MODE_TRADES))
        {
         if(OrderSymbol()==Symbol() && OrderMagicNumber()==MagicNum)
           {
            if(OrderType()==OP_BUY)
              {
               buynum++;
               buylots+=OrderLots();
               buylots1=OrderLots();
               buyprof+=(OrderProfit()+OrderCommission()+OrderSwap());

               blstop=OrderOpenPrice();
               // 多单的什么 =       bid - 多单收益/多单总手数/1 * 有效位数 
               buyavg=NormalizeDouble(Bid-buyprof/buylots/1*Point,Digits);
               bTicket_B= OrderTicket();
              }
            else
               if(OrderType()==OP_SELL)
                 {
                  sellnum++;
                  sellots+=OrderLots();
                  sellots1=OrderLots();
                  sellprof+=(OrderProfit()+OrderCommission()+OrderSwap());

                  sellavg=NormalizeDouble(Ask+sellprof/sellots/1*Point,Digits);
                  slstop=OrderOpenPrice();
                  STicket_S=OrderTicket();
                 }
           }
        }
     }
   return (0);

  }




//=================平仓部份==================================================================

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
void CloseOrders1(int Ai_0)
  {
   int ping =0;
   for(int Li_4 = OrdersTotal() - 1; Li_4 >= 0; Li_4--)
     {
      if(OrderSelect(Li_4, SELECT_BY_POS, MODE_TRADES))
        {
         if(OrderSymbol() == Symbol() && OrderMagicNumber() == MagicNum)
            if(OrderType() == Ai_0 && Ask - OrderOpenPrice()>= tpPoint*Point ) // 止盈方法
               ping = OrderClose(OrderTicket(), OrderLots(), OrderClosePrice(), 300, Yellow);
        }
     }
  }

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
void CloseOrders2(int Ai_0)
  {
   int ping =0;
   for(int Li_4 = OrdersTotal() - 1; Li_4 >= 0; Li_4--)
     {
      if(OrderSelect(Li_4, SELECT_BY_POS, MODE_TRADES))
        {
         if(OrderSymbol() == Symbol() && OrderMagicNumber() == MagicNum)
            if(OrderType() == Ai_0 &&  OrderOpenPrice()-Bid >= tpPoint*Point ) // 止盈方法
               ping = OrderClose(OrderTicket(), OrderLots(), OrderClosePrice(), 300, Yellow);
        }
     }
  }


void CloseBuy()
  {
   for(int Li_4 = OrdersTotal() - 1; Li_4 >= 0; Li_4--)
     {
      if(OrderSelect(Li_4, SELECT_BY_POS, MODE_TRADES))
        {
         if(OrderSymbol() == Symbol() && OrderMagicNumber() == MagicNum  && OrderType() == OP_BUY){
         
            double bandsUpper = iBands(NULL,0,20,2,0,PRICE_CLOSE,MODE_UPPER,0);
            double bandsLower = iBands(NULL,0,20,2,0,PRICE_CLOSE,MODE_LOWER,0);
            //离场
            if(Bid >= bandsUpper || Bid  < bandsLower){
               OrderClose(OrderTicket(), OrderLots(), Bid, 300, Yellow);
            }
         }
         
        }
     }
  }
  
  
void CloseSell()
  {
   for(int Li_4 = OrdersTotal() - 1; Li_4 >= 0; Li_4--)
     {
      if(OrderSelect(Li_4, SELECT_BY_POS, MODE_TRADES))
        {
         if(OrderSymbol() == Symbol() && OrderMagicNumber() == MagicNum && OrderType() == OP_SELL ){
         
            double bandsUpper = iBands(NULL,0,20,2,0,PRICE_CLOSE,MODE_UPPER,0);
            double bandsLower = iBands(NULL,0,20,2,0,PRICE_CLOSE,MODE_LOWER,0);
            if(Ask <= bandsLower || Ask  >= bandsUpper){
               OrderClose(OrderTicket(), OrderLots(), Ask, 300, Yellow);
            }
          
         }
         
        }
     }
  }

//+------------------------------------------------------------------+
//价差检查
void checkSpread(){

    //获取当前产品价差
   spread=MarketInfo(Symbol(), MODE_SPREAD);

   //如果价差超过最大价差限制，关闭交易开关
   if(spread > pointLimit)
     {
      //Print(TimeToStr(TimeCurrent(),TIME_DATE|TIME_SECONDS)+" ,点差过高! 当前点差: "+spread);
      AllowOpen=false;
     }
   else
     {
      Comment("");
      AllowOpen=true;
     }

}
