"""
Auto Portfolio Rebalancer - Automatic Position Management

This component automatically executes trades based on alerts from the
Continuous Portfolio Monitor. It turns recommendations into actions.

Features:
1. Auto-execute trades when alerts trigger
2. Safety limits to prevent over-trading
3. Strategy-aware rebalancing
4. Telegram notifications for all actions
5. Dry-run mode for testing
"""

import os
import sys
import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from storage.database import SessionLocal
from services.position_service import PositionService
from services.account_service import AccountService
from services.continuous_monitor import (
    ContinuousPortfolioMonitor, 
    Alert, 
    AlertType, 
    ActionUrgency,
    PortfolioSnapshot,
    PositionUpdate
)
from services.portfolio_risk_service import PositionAction, RiskLevel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RebalanceAction(Enum):
    """Types of rebalancing actions"""
    BUY = "buy"
    SELL = "sell"
    SELL_ALL = "sell_all"
    NO_ACTION = "no_action"


@dataclass
class TradeExecution:
    """Record of an executed trade"""
    timestamp: datetime
    symbol: str
    action: RebalanceAction
    quantity: float
    price: float
    total_value: float
    reason: str
    alert_type: Optional[AlertType]
    success: bool
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "symbol": self.symbol,
            "action": self.action.value,
            "quantity": self.quantity,
            "price": self.price,
            "total_value": self.total_value,
            "reason": self.reason,
            "alert_type": self.alert_type.value if self.alert_type else None,
            "success": self.success,
            "error": self.error
        }


@dataclass
class RebalanceConfig:
    """Configuration for auto-rebalancing"""
    enabled: bool = True
    dry_run: bool = True  # If True, only simulate trades
    
    # Safety limits
    max_daily_trades: int = 10
    max_single_trade_pct: float = 25.0  # Max % of position to trade at once
    min_trade_value: float = 100.0  # Minimum trade value
    cooldown_minutes: int = 15  # Wait between trades on same symbol
    
    # Alert thresholds for auto-action
    auto_exit_loss_pct: float = -15.0  # Auto-exit if loss exceeds this
    auto_reduce_gain_pct: float = 30.0  # Auto-take-profits at this gain
    auto_reduce_concentration_pct: float = 30.0  # Reduce if > this % of portfolio
    
    # Position sizing for new buys
    target_position_pct: float = 5.0  # Target size as % of portfolio
    max_position_pct: float = 10.0  # Never exceed this
    
    # Urgency thresholds
    act_on_immediate: bool = True
    act_on_high: bool = True
    act_on_medium: bool = False
    act_on_low: bool = False


@dataclass
class RebalanceResult:
    """Result of a rebalancing cycle"""
    timestamp: datetime
    trades_executed: List[TradeExecution]
    alerts_processed: int
    portfolio_before: Optional[PortfolioSnapshot]
    portfolio_after: Optional[PortfolioSnapshot]
    dry_run: bool
    
    def summary(self) -> str:
        executed = [t for t in self.trades_executed if t.success]
        total_value = sum(t.total_value for t in executed)
        return (
            f"Rebalance {'(DRY RUN) ' if self.dry_run else ''}"
            f"at {self.timestamp.strftime('%H:%M:%S')}: "
            f"{len(executed)} trades, ${total_value:,.2f} total"
        )


class AutoPortfolioRebalancer:
    """
    Automatic portfolio rebalancer that executes trades based on alerts.
    
    Integrates with ContinuousPortfolioMonitor to automatically:
    - Exit losing positions when stop-loss is hit
    - Take profits on big winners
    - Reduce concentrated positions
    - Deploy idle capital to opportunities
    """
    
    def __init__(
        self,
        account_id: str,
        config: Optional[RebalanceConfig] = None,
        on_trade: Optional[Callable[[TradeExecution], None]] = None,
        on_rebalance: Optional[Callable[[RebalanceResult], None]] = None
    ):
        self.account_id = account_id
        self.config = config or RebalanceConfig()
        self.on_trade = on_trade
        self.on_rebalance = on_rebalance
        
        # State tracking
        self._trade_history: List[TradeExecution] = []
        self._daily_trade_count = 0
        self._last_trade_time: Dict[str, datetime] = {}  # Per-symbol cooldown
        self._last_reset_date = datetime.now().date()
        
        # Monitor integration
        self._monitor: Optional[ContinuousPortfolioMonitor] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
    
    def start(self, monitor: ContinuousPortfolioMonitor):
        """Start auto-rebalancing, connected to a monitor"""
        self._monitor = monitor
        self._running = True
        
        # Set up monitor callbacks
        original_on_alert = monitor.on_alert
        
        def on_alert_with_rebalance(alert: Alert):
            if original_on_alert:
                original_on_alert(alert)
            self._handle_alert(alert)
        
        monitor.on_alert = on_alert_with_rebalance
        
        logger.info(f"🔄 Auto-rebalancer started for account {self.account_id}")
        logger.info(f"   Mode: {'DRY RUN' if self.config.dry_run else 'LIVE TRADING'}")
    
    def stop(self):
        """Stop auto-rebalancing"""
        self._running = False
        logger.info(f"⏹️ Auto-rebalancer stopped")
    
    def _reset_daily_limits(self):
        """Reset daily limits if new day"""
        today = datetime.now().date()
        if today > self._last_reset_date:
            self._daily_trade_count = 0
            self._last_reset_date = today
    
    def _can_trade(self, symbol: str) -> tuple:
        """Check if trading is allowed for this symbol"""
        self._reset_daily_limits()
        
        # Check daily limit
        if self._daily_trade_count >= self.config.max_daily_trades:
            return False, "Daily trade limit reached"
        
        # Check cooldown
        if symbol in self._last_trade_time:
            elapsed = (datetime.now() - self._last_trade_time[symbol]).total_seconds() / 60
            if elapsed < self.config.cooldown_minutes:
                return False, f"Cooldown active ({self.config.cooldown_minutes - elapsed:.0f} min left)"
        
        return True, "OK"
    
    def _handle_alert(self, alert: Alert):
        """Handle an alert from the monitor"""
        if not self._running or not self.config.enabled:
            return
        
        # Check urgency threshold
        should_act = (
            (alert.urgency == ActionUrgency.IMMEDIATE and self.config.act_on_immediate) or
            (alert.urgency == ActionUrgency.HIGH and self.config.act_on_high) or
            (alert.urgency == ActionUrgency.MEDIUM and self.config.act_on_medium) or
            (alert.urgency == ActionUrgency.LOW and self.config.act_on_low)
        )
        
        if not should_act:
            logger.debug(f"Skipping alert (urgency {alert.urgency.value}): {alert.title}")
            return
        
        # Determine action based on alert type
        if alert.alert_type == AlertType.STOP_LOSS_HIT:
            self._handle_stop_loss(alert)
        elif alert.alert_type == AlertType.TAKE_PROFIT:
            self._handle_take_profit(alert)
        elif alert.alert_type == AlertType.CONCENTRATION:
            self._handle_concentration(alert)
        elif alert.alert_type == AlertType.RISK_THRESHOLD:
            self._handle_risk_threshold(alert)
        elif alert.alert_type == AlertType.IDLE_CAPITAL:
            self._handle_idle_capital(alert)
    
    def _handle_stop_loss(self, alert: Alert):
        """Handle stop-loss alert - exit or reduce position"""
        symbol = alert.symbol
        if not symbol:
            return
        
        pnl_pct = alert.data.get('pnl_pct', 0)
        current_price = alert.data.get('current_price', 0)
        
        # Determine action severity
        if pnl_pct < self.config.auto_exit_loss_pct:
            # Full exit - critical loss
            self._execute_trade(
                symbol=symbol,
                action=RebalanceAction.SELL_ALL,
                reason=f"Stop-loss triggered at {pnl_pct:.1f}% loss",
                alert_type=alert.alert_type,
                price=current_price
            )
        else:
            # Partial reduce - moderate loss
            self._execute_trade(
                symbol=symbol,
                action=RebalanceAction.SELL,
                quantity_pct=50.0,  # Reduce by 50%
                reason=f"Reducing exposure due to {pnl_pct:.1f}% loss",
                alert_type=alert.alert_type,
                price=current_price
            )
    
    def _handle_take_profit(self, alert: Alert):
        """Handle take-profit alert - reduce position to lock gains"""
        symbol = alert.symbol
        if not symbol:
            return
        
        pnl_pct = alert.data.get('pnl_pct', 0)
        current_price = alert.data.get('current_price', 0)
        
        if pnl_pct > self.config.auto_reduce_gain_pct:
            # Take partial profits
            reduce_pct = min(50.0, self.config.max_single_trade_pct)
            self._execute_trade(
                symbol=symbol,
                action=RebalanceAction.SELL,
                quantity_pct=reduce_pct,
                reason=f"Taking profits at {pnl_pct:.1f}% gain",
                alert_type=alert.alert_type,
                price=current_price
            )
    
    def _handle_concentration(self, alert: Alert):
        """Handle concentration alert - reduce oversized position"""
        symbol = alert.symbol
        if not symbol:
            return
        
        concentration = alert.data.get('concentration_pct', 0)
        current_price = alert.data.get('current_price', 0)
        
        if concentration > self.config.auto_reduce_concentration_pct:
            # Calculate how much to reduce
            target_pct = self.config.target_position_pct
            reduce_pct = ((concentration - target_pct) / concentration) * 100
            reduce_pct = min(reduce_pct, self.config.max_single_trade_pct)
            
            self._execute_trade(
                symbol=symbol,
                action=RebalanceAction.SELL,
                quantity_pct=reduce_pct,
                reason=f"Reducing concentration from {concentration:.1f}% to ~{target_pct:.1f}%",
                alert_type=alert.alert_type,
                price=current_price
            )
    
    def _handle_risk_threshold(self, alert: Alert):
        """Handle critical risk - emergency exit"""
        symbol = alert.symbol
        if not symbol:
            return
        
        current_price = alert.data.get('current_price', 0)
        
        # Critical risk = full exit
        self._execute_trade(
            symbol=symbol,
            action=RebalanceAction.SELL_ALL,
            reason="Critical risk threshold exceeded",
            alert_type=alert.alert_type,
            price=current_price
        )
    
    def _handle_idle_capital(self, alert: Alert):
        """Handle idle capital - could deploy to opportunities"""
        # For now, just log - could add auto-buy logic later
        idle_pct = alert.data.get('idle_pct', 0)
        logger.info(f"📊 Idle capital detected: {idle_pct:.1f}% - Consider deploying")
    
    def _execute_trade(
        self,
        symbol: str,
        action: RebalanceAction,
        reason: str,
        alert_type: Optional[AlertType] = None,
        price: float = 0,
        quantity_pct: float = 100.0
    ):
        """Execute a trade (or simulate in dry-run mode)"""
        # Check if we can trade
        can_trade, message = self._can_trade(symbol)
        if not can_trade:
            logger.warning(f"⚠️ Cannot trade {symbol}: {message}")
            return
        
        # Get position details
        db = SessionLocal()
        try:
            position_service = PositionService(db)
            positions = position_service.get_positions_by_account(self.account_id)
            
            position = None
            for p in positions:
                pos_symbol = p.symbol.ticker if hasattr(p, 'symbol') and p.symbol else ""
                if pos_symbol.upper() == symbol.upper():
                    position = p
                    break
            
            if not position and action in [RebalanceAction.SELL, RebalanceAction.SELL_ALL]:
                logger.warning(f"⚠️ No position found for {symbol}")
                return
            
            # Calculate quantity
            if action == RebalanceAction.SELL_ALL:
                quantity = float(position.quantity) if position else 0
            elif action == RebalanceAction.SELL:
                full_quantity = float(position.quantity) if position else 0
                quantity = full_quantity * (quantity_pct / 100.0)
            else:
                quantity = 0  # TODO: Calculate buy quantity
            
            # Apply max single trade limit
            if position:
                max_quantity = float(position.quantity) * (self.config.max_single_trade_pct / 100.0)
                quantity = min(quantity, max_quantity)
            
            # Calculate value
            trade_value = quantity * price if price > 0 else 0
            
            # Check minimum trade value
            if trade_value < self.config.min_trade_value and action != RebalanceAction.SELL_ALL:
                logger.info(f"📊 Trade too small for {symbol}: ${trade_value:.2f}")
                return
            
            # Create trade execution record
            execution = TradeExecution(
                timestamp=datetime.now(),
                symbol=symbol,
                action=action,
                quantity=quantity,
                price=price,
                total_value=trade_value,
                reason=reason,
                alert_type=alert_type,
                success=True,
                error=None
            )
            
            if self.config.dry_run:
                # Simulate trade
                logger.info(
                    f"🔄 [DRY RUN] Would {action.value} {quantity:.2f} {symbol} "
                    f"@ ${price:.2f} = ${trade_value:,.2f}"
                )
                logger.info(f"   Reason: {reason}")
            else:
                # Execute real trade
                try:
                    self._execute_real_trade(db, position, action, quantity, price)
                    logger.info(
                        f"✅ EXECUTED: {action.value} {quantity:.2f} {symbol} "
                        f"@ ${price:.2f} = ${trade_value:,.2f}"
                    )
                except Exception as e:
                    execution.success = False
                    execution.error = str(e)
                    logger.error(f"❌ Trade failed for {symbol}: {e}")
            
            # Update state
            self._trade_history.append(execution)
            self._daily_trade_count += 1
            self._last_trade_time[symbol] = datetime.now()
            
            # Callback
            if self.on_trade:
                self.on_trade(execution)
                
        finally:
            db.close()
    
    def _execute_real_trade(
        self,
        db: Session,
        position: Any,
        action: RebalanceAction,
        quantity: float,
        price: float
    ):
        """Execute a real trade in the database"""
        from storage.models import Order
        from datetime import datetime
        
        if action in [RebalanceAction.SELL, RebalanceAction.SELL_ALL]:
            order = Order(
                account_id=self.account_id,
                symbol_id=position.symbol_id,
                order_type="sell",
                quantity=quantity,
                price=price,
                status="filled",
                created_at=datetime.now(),
                filled_at=datetime.now()
            )
            db.add(order)
            
            # Update position
            position.quantity = float(position.quantity) - quantity
            if position.quantity <= 0:
                db.delete(position)
            
            db.commit()
    
    def get_trade_history(self, limit: int = 20) -> List[TradeExecution]:
        """Get recent trade history"""
        return self._trade_history[-limit:]
    
    def get_daily_stats(self) -> Dict[str, Any]:
        """Get daily trading statistics"""
        self._reset_daily_limits()
        
        today_trades = [
            t for t in self._trade_history 
            if t.timestamp.date() == datetime.now().date()
        ]
        
        return {
            "trades_today": len(today_trades),
            "trades_remaining": self.config.max_daily_trades - self._daily_trade_count,
            "total_volume": sum(t.total_value for t in today_trades if t.success),
            "successful": sum(1 for t in today_trades if t.success),
            "failed": sum(1 for t in today_trades if not t.success),
            "dry_run_mode": self.config.dry_run
        }
    
    def manual_rebalance(self) -> RebalanceResult:
        """Trigger a manual rebalance based on current state"""
        if not self._monitor:
            raise ValueError("Monitor not connected. Call start() first.")
        
        snapshot_before = self._monitor.get_current_state()
        trades_before = len(self._trade_history)
        
        # Process all current alerts
        if snapshot_before:
            for alert in snapshot_before.alerts:
                self._handle_alert(alert)
        
        snapshot_after = self._monitor.get_current_state()
        new_trades = self._trade_history[trades_before:]
        
        result = RebalanceResult(
            timestamp=datetime.now(),
            trades_executed=new_trades,
            alerts_processed=len(snapshot_before.alerts) if snapshot_before else 0,
            portfolio_before=snapshot_before,
            portfolio_after=snapshot_after,
            dry_run=self.config.dry_run
        )
        
        if self.on_rebalance:
            self.on_rebalance(result)
        
        return result


# ==================== FACTORY ====================

def create_auto_rebalancer(
    account_id: str,
    dry_run: bool = True,
    on_trade: Optional[Callable[[TradeExecution], None]] = None
) -> AutoPortfolioRebalancer:
    """Create an auto-rebalancer with default config"""
    
    config = RebalanceConfig(
        enabled=True,
        dry_run=dry_run,
        max_daily_trades=10,
        max_single_trade_pct=25.0,
        cooldown_minutes=15,
        auto_exit_loss_pct=-15.0,
        auto_reduce_gain_pct=30.0,
        auto_reduce_concentration_pct=30.0,
        act_on_immediate=True,
        act_on_high=True,
        act_on_medium=False,
        act_on_low=False
    )
    
    def default_on_trade(trade: TradeExecution):
        emoji = "🟢" if trade.success else "🔴"
        mode = "[DRY]" if config.dry_run else "[LIVE]"
        logger.info(
            f"{emoji} {mode} {trade.action.value.upper()} {trade.quantity:.2f} "
            f"{trade.symbol} @ ${trade.price:.2f}"
        )
    
    return AutoPortfolioRebalancer(
        account_id=account_id,
        config=config,
        on_trade=on_trade or default_on_trade
    )


# ==================== COMBINED SYSTEM ====================

class ContinuousRebalancingSystem:
    """
    Complete system combining monitoring + auto-rebalancing.
    
    This is the main entry point for the hackathon demo.
    """
    
    def __init__(
        self,
        account_id: str,
        monitor_interval: int = 60,
        dry_run: bool = True,
        telegram_notify: Optional[Callable[[str], None]] = None
    ):
        self.account_id = account_id
        self.telegram_notify = telegram_notify
        
        # Create monitor
        self.monitor = ContinuousPortfolioMonitor(
            account_id=account_id,
            check_interval_seconds=monitor_interval,
            on_alert=self._on_alert,
            on_update=self._on_update
        )
        
        # Create rebalancer
        self.rebalancer = create_auto_rebalancer(
            account_id=account_id,
            dry_run=dry_run,
            on_trade=self._on_trade
        )
    
    def _on_alert(self, alert: Alert):
        """Handle alert - notify user"""
        if self.telegram_notify:
            urgency_emoji = {
                "immediate": "🔴",
                "high": "🟠", 
                "medium": "🟡",
                "low": "🟢"
            }.get(alert.urgency.value, "⚪")
            
            message = (
                f"{urgency_emoji} **Alert: {alert.title}**\n"
                f"{alert.message}"
            )
            self.telegram_notify(message)
    
    def _on_update(self, snapshot: PortfolioSnapshot):
        """Handle portfolio update"""
        logger.debug(f"Portfolio update: {snapshot.position_count} positions, risk={snapshot.risk_level.value}")
    
    def _on_trade(self, trade: TradeExecution):
        """Handle trade execution - notify user"""
        if self.telegram_notify:
            emoji = "✅" if trade.success else "❌"
            mode = "(Simulated)" if self.rebalancer.config.dry_run else ""
            
            message = (
                f"{emoji} **Trade Executed {mode}**\n"
                f"{trade.action.value.upper()} {trade.quantity:.2f} {trade.symbol}\n"
                f"Price: ${trade.price:.2f}\n"
                f"Value: ${trade.total_value:,.2f}\n"
                f"Reason: {trade.reason}"
            )
            self.telegram_notify(message)
    
    def start(self):
        """Start the complete system"""
        logger.info("=" * 50)
        logger.info("🚀 Starting Continuous Rebalancing System")
        logger.info(f"   Account: {self.account_id}")
        logger.info(f"   Mode: {'DRY RUN' if self.rebalancer.config.dry_run else 'LIVE'}")
        logger.info("=" * 50)
        
        # Start monitor first
        self.monitor.start()
        
        # Connect rebalancer to monitor
        self.rebalancer.start(self.monitor)
    
    def stop(self):
        """Stop the complete system"""
        self.rebalancer.stop()
        self.monitor.stop()
        logger.info("⏹️ System stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        snapshot = self.monitor.get_current_state()
        daily_stats = self.rebalancer.get_daily_stats()
        
        return {
            "account_id": self.account_id,
            "monitoring": self.monitor._running,
            "rebalancing": self.rebalancer._running,
            "dry_run": self.rebalancer.config.dry_run,
            "portfolio": snapshot.to_dict() if snapshot else None,
            "daily_trades": daily_stats,
            "recent_trades": [t.to_dict() for t in self.rebalancer.get_trade_history(5)]
        }
    
    def trigger_rebalance(self) -> RebalanceResult:
        """Manually trigger a rebalance"""
        return self.rebalancer.manual_rebalance()


# ==================== DEMO ====================

if __name__ == "__main__":
    print("🤖 Auto Portfolio Rebalancer Demo")
    print("=" * 50)
    
    # Create system in dry-run mode
    system = ContinuousRebalancingSystem(
        account_id="demo",
        monitor_interval=30,
        dry_run=True,  # Safe mode - no real trades
        telegram_notify=lambda msg: print(f"📱 TELEGRAM: {msg}")
    )
    
    # Start system
    system.start()
    
    print("\n⏱️ Running for 2 minutes (Ctrl+C to stop)...")
    print("   Monitoring positions and auto-rebalancing on alerts\n")
    
    try:
        import time
        for i in range(4):  # 4 x 30 seconds = 2 minutes
            time.sleep(30)
            status = system.get_status()
            print(f"\n📊 Status Update ({i+1}/4):")
            print(f"   Trades today: {status['daily_trades']['trades_today']}")
            print(f"   Trades remaining: {status['daily_trades']['trades_remaining']}")
    except KeyboardInterrupt:
        print("\n⏹️ Stopping...")
    finally:
        system.stop()
        print("Done!")
