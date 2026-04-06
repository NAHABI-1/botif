# Deployment

## Environments
- Local: development, backtesting, paper.
- Staging: demo accounts and soak testing.
- Production: live trading (disabled by default).

## Support Services
Start Postgres with:
```bash
docker compose -f infra/docker-compose.support.yml up -d
```

## MT5 Terminal (Windows Host)
MT5 terminal is not containerized. Install and run it on the Windows VPS:
- EA path: `C:\Users\<User>\AppData\Roaming\MetaQuotes\Terminal\<TerminalHash>\MQL5\Experts\ProductionTraderEA.mq5`
- Include path: `C:\Users\<User>\AppData\Roaming\MetaQuotes\Terminal\<TerminalHash>\MQL5\Include\ProductionTrader\`

## Service Placement
- Worker runs on the same Windows host as MT5 terminal.
- API and dashboard can run on a separate Linux host or on the same VPS.

## Startup Order
1. Postgres
2. API
3. Worker
4. Dashboard

## Security Notes
- Restrict inbound ports to trusted IPs.
- Keep secrets out of repo; use environment variables or secret manager.
- Apply OS updates monthly and reboot during maintenance windows.
