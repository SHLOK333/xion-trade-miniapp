"""
Portfolio Risk Service - Continuous Decision-Making for Risk-Aware Trading

This service implements the core hackathon requirements:
1. Continuously assess risk, capital, and potential returns for open positions
2. Recommend actions: hold, reduce, exit, or reallocate capital
3. Manage multiple positions together to balance risk and maximize performance
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session

from services.position_service import PositionService
from services.account_service import AccountService


class PositionAction(Enum):
    """Recommended actions for a position"""
    HOLD = "hold"
    REDUCE = "reduce"  # Partial exit
    EXIT = "exit"      # Full exit
    ADD = "add"        # Increase position
    REALLOCATE = "reallocate"  # Move capital to better opportunity


class RiskLevel(Enum):
    """Risk levels for positions and portfolio"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PositionRiskAssessment:
    """Risk assessment for a single position"""
    symbol: str
    symbol_id: int
    quantity: float
    entry_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    
    # Risk metrics
    risk_level: RiskLevel = RiskLevel.MODERATE
    volatility_score: float = 0.0  # 0-100
    concentration_risk: float = 0.0  # % of portfolio
    drawdown_from_high: float = 0.0
    days_held: int = 0
    
    # AI analysis
    recommended_action: PositionAction = PositionAction.HOLD
    action_reason: str = ""
    target_allocation: float = 0.0  # Suggested % of portfolio
    stop_loss_price: float = 0.0
    take_profit_price: float = 0.0
    confidence_score: float = 0.0  # 0-1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "symbol_id": self.symbol_id,
            "quantity": self.quantity,
            "entry_price": self.entry_price,
            "current_price": self.current_price,
            "market_value": self.market_value,
            "unrealized_pnl": self.unrealized_pnl,
            "unrealized_pnl_pct": self.unrealized_pnl_pct,
            "risk_level": self.risk_level.value,
            "volatility_score": self.volatility_score,
            "concentration_risk": self.concentration_risk,
            "drawdown_from_high": self.drawdown_from_high,
            "days_held": self.days_held,
            "recommended_action": self.recommended_action.value,
            "action_reason": self.action_reason,
            "target_allocation": self.target_allocation,
            "stop_loss_price": self.stop_loss_price,
            "take_profit_price": self.take_profit_price,
            "confidence_score": self.confidence_score
        }


@dataclass
class PortfolioRiskAssessment:
    """Portfolio-level risk assessment"""
    account_id: str
    total_value: float
    cash_available: float
    invested_value: float
    total_unrealized_pnl: float
    
    # Portfolio metrics
    overall_risk_level: RiskLevel = RiskLevel.MODERATE
    diversification_score: float = 0.0  # 0-100
    concentration_warning: bool = False
    max_position_concentration: float = 0.0
    correlation_risk: float = 0.0
    
    # Position assessments
    positions: List[PositionRiskAssessment] = field(default_factory=list)
    
    # Recommendations
    rebalance_needed: bool = False
    capital_at_risk: float = 0.0
    suggested_actions: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "account_id": self.account_id,
            "total_value": self.total_value,
            "cash_available": self.cash_available,
            "invested_value": self.invested_value,
            "total_unrealized_pnl": self.total_unrealized_pnl,
            "overall_risk_level": self.overall_risk_level.value,
            "diversification_score": self.diversification_score,
            "concentration_warning": self.concentration_warning,
            "max_position_concentration": self.max_position_concentration,
            "correlation_risk": self.correlation_risk,
            "positions": [p.to_dict() for p in self.positions],
            "rebalance_needed": self.rebalance_needed,
            "capital_at_risk": self.capital_at_risk,
            "suggested_actions": self.suggested_actions
        }


@dataclass
class ReallocationSuggestion:
    """Capital reallocation suggestion"""
    from_symbol: Optional[str]
    to_symbol: Optional[str]
    amount: float
    reason: str
    priority: int  # 1-5, 1 being highest
    expected_benefit: str
    risk_impact: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_symbol": self.from_symbol,
            "to_symbol": self.to_symbol,
            "amount": self.amount,
            "reason": self.reason,
            "priority": self.priority,
            "expected_benefit": self.expected_benefit,
            "risk_impact": self.risk_impact
        }


class PortfolioRiskService:
    """
    Service for continuous portfolio risk assessment and management.
    
    This implements the hackathon's core requirement:
    "Continuously assess risk, capital, and potential returns for open positions"
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.position_service = PositionService(db)
        self.account_service = AccountService(db)
        
        # Risk thresholds (configurable)
        self.max_position_concentration = 0.25  # 25% max per position
        self.stop_loss_threshold = -0.10  # -10% triggers exit consideration
        self.take_profit_threshold = 0.20  # +20% triggers profit taking
        self.high_volatility_threshold = 70  # Volatility score
        
    def assess_portfolio_risk(self, account_id: str) -> PortfolioRiskAssessment:
        """
        Perform comprehensive portfolio risk assessment.
        Returns assessment with recommendations for all positions.
        """
        # Get account and positions
        account = self.account_service.get_account_by_id(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        positions = self.position_service.get_positions_by_account(account_id)
        
        # Calculate portfolio totals
        total_invested = sum(
            (p.quantity or 0) * (p.current_price or p.average_entry_price or 0)
            for p in positions
        )
        cash_available = float(account.balance) if account.balance else 0
        total_value = total_invested + cash_available
        
        # Assess each position
        position_assessments = []
        for position in positions:
            if position.quantity and position.quantity > 0:
                assessment = self._assess_position(position, total_value)
                position_assessments.append(assessment)
        
        # Calculate portfolio-level metrics
        portfolio_assessment = PortfolioRiskAssessment(
            account_id=account_id,
            total_value=total_value,
            cash_available=cash_available,
            invested_value=total_invested,
            total_unrealized_pnl=sum(p.unrealized_pnl for p in position_assessments),
            positions=position_assessments
        )
        
        # Analyze portfolio composition
        self._analyze_portfolio_composition(portfolio_assessment)
        
        # Generate action recommendations
        self._generate_recommendations(portfolio_assessment)
        
        return portfolio_assessment
    
    def _assess_position(self, position, total_portfolio_value: float) -> PositionRiskAssessment:
        """Assess risk for a single position"""
        quantity = float(position.quantity or 0)
        entry_price = float(position.average_entry_price or 0)
        current_price = float(position.current_price or entry_price)
        
        market_value = quantity * current_price
        cost_basis = quantity * entry_price
        unrealized_pnl = market_value - cost_basis
        unrealized_pnl_pct = (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0
        
        # Calculate concentration risk
        concentration = (market_value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
        
        # Determine risk level based on multiple factors
        risk_level = self._calculate_risk_level(unrealized_pnl_pct, concentration)
        
        # Determine recommended action
        action, reason = self._determine_action(
            unrealized_pnl_pct, concentration, risk_level
        )
        
        # Get symbol name (if available)
        symbol_name = position.symbol.ticker if hasattr(position, 'symbol') and position.symbol else f"ID:{position.symbol_id}"
        
        return PositionRiskAssessment(
            symbol=symbol_name,
            symbol_id=position.symbol_id,
            quantity=quantity,
            entry_price=entry_price,
            current_price=current_price,
            market_value=market_value,
            unrealized_pnl=unrealized_pnl,
            unrealized_pnl_pct=unrealized_pnl_pct,
            risk_level=risk_level,
            concentration_risk=concentration,
            recommended_action=action,
            action_reason=reason,
            target_allocation=min(concentration, self.max_position_concentration * 100),
            stop_loss_price=entry_price * (1 + self.stop_loss_threshold),
            take_profit_price=entry_price * (1 + self.take_profit_threshold),
            confidence_score=0.7  # Will be enhanced with AI
        )
    
    def _calculate_risk_level(self, pnl_pct: float, concentration: float) -> RiskLevel:
        """Calculate risk level for a position"""
        # High loss = high risk
        if pnl_pct < -20:
            return RiskLevel.CRITICAL
        if pnl_pct < -10:
            return RiskLevel.HIGH
        
        # High concentration = higher risk
        if concentration > 40:
            return RiskLevel.HIGH
        if concentration > 25:
            return RiskLevel.MODERATE
        
        # Moderate profit but could reverse
        if pnl_pct > 30:
            return RiskLevel.MODERATE  # Profit taking territory
        
        return RiskLevel.LOW
    
    def _determine_action(
        self, 
        pnl_pct: float, 
        concentration: float,
        risk_level: RiskLevel
    ) -> Tuple[PositionAction, str]:
        """Determine recommended action for a position"""
        
        # Critical loss - consider exit
        if pnl_pct < self.stop_loss_threshold * 100:
            return PositionAction.EXIT, f"Stop loss triggered: {pnl_pct:.1f}% loss exceeds {self.stop_loss_threshold*100}% threshold"
        
        # Large profit - consider taking some
        if pnl_pct > self.take_profit_threshold * 100:
            return PositionAction.REDUCE, f"Take profit opportunity: {pnl_pct:.1f}% gain exceeds {self.take_profit_threshold*100}% threshold"
        
        # Over-concentrated - reduce to manage risk
        if concentration > self.max_position_concentration * 100:
            return PositionAction.REDUCE, f"Position too concentrated at {concentration:.1f}% of portfolio (max {self.max_position_concentration*100}%)"
        
        # Critical risk level
        if risk_level == RiskLevel.CRITICAL:
            return PositionAction.EXIT, "Critical risk level - recommend full exit"
        
        # High risk - consider reducing
        if risk_level == RiskLevel.HIGH:
            return PositionAction.REDUCE, "High risk level - consider reducing exposure"
        
        return PositionAction.HOLD, "Position within acceptable risk parameters"
    
    def _analyze_portfolio_composition(self, assessment: PortfolioRiskAssessment):
        """Analyze portfolio composition and set portfolio-level metrics"""
        if not assessment.positions:
            assessment.diversification_score = 100  # All cash
            assessment.overall_risk_level = RiskLevel.LOW
            return
        
        # Check diversification (more positions = more diversified)
        num_positions = len(assessment.positions)
        if num_positions >= 10:
            assessment.diversification_score = 90
        elif num_positions >= 5:
            assessment.diversification_score = 70
        elif num_positions >= 3:
            assessment.diversification_score = 50
        else:
            assessment.diversification_score = 30
        
        # Find max concentration
        concentrations = [p.concentration_risk for p in assessment.positions]
        assessment.max_position_concentration = max(concentrations) if concentrations else 0
        
        # Check for concentration warnings
        if assessment.max_position_concentration > self.max_position_concentration * 100:
            assessment.concentration_warning = True
            assessment.diversification_score -= 20
        
        # Calculate overall risk level
        risk_counts = {level: 0 for level in RiskLevel}
        for pos in assessment.positions:
            risk_counts[pos.risk_level] += 1
        
        if risk_counts[RiskLevel.CRITICAL] > 0:
            assessment.overall_risk_level = RiskLevel.CRITICAL
        elif risk_counts[RiskLevel.HIGH] > len(assessment.positions) * 0.3:
            assessment.overall_risk_level = RiskLevel.HIGH
        elif risk_counts[RiskLevel.MODERATE] > len(assessment.positions) * 0.5:
            assessment.overall_risk_level = RiskLevel.MODERATE
        else:
            assessment.overall_risk_level = RiskLevel.LOW
        
        # Check if rebalancing is needed
        actions_needed = [p for p in assessment.positions if p.recommended_action != PositionAction.HOLD]
        assessment.rebalance_needed = len(actions_needed) > 0
        
        # Calculate capital at risk (positions with negative P&L)
        assessment.capital_at_risk = sum(
            abs(p.unrealized_pnl) for p in assessment.positions if p.unrealized_pnl < 0
        )
    
    def _generate_recommendations(self, assessment: PortfolioRiskAssessment):
        """Generate actionable recommendations for the portfolio"""
        suggestions = []
        
        # Sort positions by urgency (risk level and action type)
        priority_order = {
            PositionAction.EXIT: 1,
            PositionAction.REDUCE: 2,
            PositionAction.REALLOCATE: 3,
            PositionAction.ADD: 4,
            PositionAction.HOLD: 5
        }
        
        sorted_positions = sorted(
            assessment.positions,
            key=lambda p: (priority_order.get(p.recommended_action, 5), -abs(p.unrealized_pnl_pct))
        )
        
        for i, pos in enumerate(sorted_positions):
            if pos.recommended_action != PositionAction.HOLD:
                suggestions.append({
                    "priority": i + 1,
                    "symbol": pos.symbol,
                    "action": pos.recommended_action.value,
                    "reason": pos.action_reason,
                    "current_value": pos.market_value,
                    "pnl_pct": pos.unrealized_pnl_pct,
                    "risk_level": pos.risk_level.value
                })
        
        # Add cash deployment suggestion if too much cash
        cash_pct = (assessment.cash_available / assessment.total_value * 100) if assessment.total_value > 0 else 0
        if cash_pct > 30:
            suggestions.append({
                "priority": len(suggestions) + 1,
                "symbol": None,
                "action": "deploy_cash",
                "reason": f"Cash position at {cash_pct:.1f}% - consider deploying to opportunities",
                "current_value": assessment.cash_available,
                "pnl_pct": 0,
                "risk_level": "low"
            })
        
        assessment.suggested_actions = suggestions
    
    def get_reallocation_suggestions(
        self, 
        account_id: str,
        opportunities: Optional[List[Dict[str, Any]]] = None
    ) -> List[ReallocationSuggestion]:
        """
        Get capital reallocation suggestions.
        
        This implements: "Recommend reallocating capital as new opportunities arise"
        """
        assessment = self.assess_portfolio_risk(account_id)
        suggestions = []
        
        # Find positions to reduce
        positions_to_reduce = [
            p for p in assessment.positions 
            if p.recommended_action in [PositionAction.REDUCE, PositionAction.EXIT]
        ]
        
        if not positions_to_reduce and not opportunities:
            return suggestions
        
        # Calculate freed capital from reductions
        freed_capital = 0
        for pos in positions_to_reduce:
            if pos.recommended_action == PositionAction.EXIT:
                amount = pos.market_value
            else:  # REDUCE
                # Reduce to target allocation
                target_value = assessment.total_value * (pos.target_allocation / 100)
                amount = max(0, pos.market_value - target_value)
            
            freed_capital += amount
            
            suggestions.append(ReallocationSuggestion(
                from_symbol=pos.symbol,
                to_symbol=None,  # Will be determined by opportunities
                amount=amount,
                reason=pos.action_reason,
                priority=1 if pos.recommended_action == PositionAction.EXIT else 2,
                expected_benefit="Reduce risk exposure",
                risk_impact=f"Reduces portfolio risk from {assessment.overall_risk_level.value}"
            ))
        
        # If we have opportunities and freed capital, suggest reallocation
        if opportunities and freed_capital > 0:
            for i, opp in enumerate(opportunities[:3]):  # Top 3 opportunities
                suggestions.append(ReallocationSuggestion(
                    from_symbol="freed_capital",
                    to_symbol=opp.get("symbol"),
                    amount=freed_capital / min(3, len(opportunities)),
                    reason=f"New opportunity: {opp.get('reason', 'AI identified opportunity')}",
                    priority=3 + i,
                    expected_benefit=opp.get("expected_return", "Potential upside"),
                    risk_impact=opp.get("risk_level", "moderate")
                ))
        
        return suggestions
    
    def get_position_recommendation(
        self,
        account_id: str,
        symbol: str
    ) -> Optional[PositionRiskAssessment]:
        """Get detailed recommendation for a specific position"""
        assessment = self.assess_portfolio_risk(account_id)
        
        for pos in assessment.positions:
            if pos.symbol.upper() == symbol.upper():
                return pos
        
        return None
