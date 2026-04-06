# Risk Model

## Principles
- Deterministic evaluation.
- No broker assumptions inside core risk.
- Safety first: safe mode and panic stop.

## Key Controls
- Daily loss cap
- Max drawdown lockout
- Max open positions
- Max symbol exposure
- Max correlated exposure (scaffold)
- Spread filter
- Slippage tolerance
- Loss streak cooldown
- Reward-to-risk minimum

## Safe Mode
Safe mode reduces position size when warning thresholds are approached without fully halting trading.

## Panic Stop
Panic stop immediately halts trading and must be manually cleared.

## Outputs
Risk evaluation returns:
- Allowed or blocked
- Halt state
- Guard outcomes and reasons
- Position sizing and protection levels
