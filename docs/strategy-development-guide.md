# Strategy Development Guide

## Goals
- Deterministic signals
- No lookahead bias
- No broker dependency in strategy code

## Structure
1. Define a parameter model using `StrategyParameters`.
2. Implement a `StrategyBase` subclass.
3. Emit signals only from closed bars.

## Example Checklist
- Use `FeatureInput` and `FeatureBar`.
- Ensure `minimum_bars` is satisfied.
- Externalize all parameters.
- Add unit tests for deterministic signals.

## Integration
- Register strategy in the strategy registry if needed.
- Use backtesting runner for validation.
