#pragma once

input bool EnableTrading = false;
input int MagicNumber = 20260406;

bool IsTradingEnabled() {
  return EnableTrading;
}
