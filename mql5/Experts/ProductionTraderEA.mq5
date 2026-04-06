//+------------------------------------------------------------------+
//| ProductionTraderEA.mq5                                           |
//+------------------------------------------------------------------+
#property strict

#include <ProductionTrader/Config.mqh>
#include <ProductionTrader/Logging.mqh>
#include <ProductionTrader/Execution.mqh>
#include <ProductionTrader/RiskChecks.mqh>
#include <ProductionTrader/ReconciliationHooks.mqh>
#include <ProductionTrader/SignalAdapter.mqh>

int OnInit() {
  LogInfo("EA initialized.");
  return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
  LogInfo("EA deinitialized.");
}

void OnTick() {
  if(!IsTradingEnabled()) {
    return;
  }
  // Keep OnTick thin: delegate to execution/risk hooks.
  ProcessTick();
}

void OnTradeTransaction(const MqlTradeTransaction& trans,
                        const MqlTradeRequest& request,
                        const MqlTradeResult& result) {
  HandleTradeTransaction(trans, request, result);
}
