"""
AI Position Advisor - Using TradingAgents for intelligent position management

This integrates TradingAgents' multi-agent debate system to provide
intelligent recommendations for managing open positions.

Key Features:
- 3-way risk debate (aggressive/neutral/conservative)
- Continuous position reassessment
- AI-powered hold/reduce/exit/reallocate recommendations
"""

import os
import sys
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from sqlalchemy.orm import Session

# Add TradingAgents to path
TRADING_AGENTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "TradingAgents"
)
if TRADING_AGENTS_PATH not in sys.path:
    sys.path.insert(0, TRADING_AGENTS_PATH)


class DebaterStance(Enum):
    """Risk debater stances from TradingAgents"""
    AGGRESSIVE = "aggressive"  # High risk tolerance, maximize returns
    NEUTRAL = "neutral"        # Balanced approach
    CONSERVATIVE = "conservative"  # Risk averse, preserve capital


@dataclass
class DebateArgument:
    """An argument from one of the risk debaters"""
    stance: DebaterStance
    position_action: str  # hold, reduce, exit, add
    reasoning: str
    confidence: float  # 0-1
    key_points: List[str]


@dataclass
class RiskDebateResult:
    """Result of the 3-way risk debate"""
    symbol: str
    arguments: List[DebateArgument]
    final_decision: str  # hold, reduce, exit, add
    final_reasoning: str
    risk_score: float  # 0-100
    debate_summary: str
    timestamp: datetime


class AIPositionAdvisor:
    """
    AI-powered position advisor using TradingAgents' multi-agent system.
    
    This implements the hackathon requirement:
    "Focus on reasoning and adaptability, not fixed strategies"
    """
    
    def __init__(self, db_session: Session = None, config: Dict[str, Any] = None):
        self.db_session = db_session
        self.config = config or self._get_default_config()
        self._trading_graph = None
        self._llm = None
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "llm_provider": "openai",
            "deep_think_llm": "gpt-4o-mini",
            "quick_think_llm": "gpt-4o-mini",
            "backend_url": None,
            "max_debate_rounds": 2,
        }
    
    def _get_llm(self):
        """Initialize LLM for position analysis"""
        if self._llm is None:
            try:
                from langchain_openai import ChatOpenAI
                self._llm = ChatOpenAI(
                    model=self.config.get("quick_think_llm", "gpt-4o-mini"),
                    temperature=0.3
                )
            except ImportError:
                raise ImportError("langchain-openai not installed")
        return self._llm
    
    def analyze_position_with_debate(
        self,
        symbol: str,
        position_data: Dict[str, Any],
        market_context: Optional[Dict[str, Any]] = None
    ) -> RiskDebateResult:
        """
        Analyze a position using 3-way risk debate (aggressive/neutral/conservative).
        
        This mirrors TradingAgents' risk debate system for position management.
        """
        llm = self._get_llm()
        
        # Prepare position context
        position_context = self._prepare_position_context(position_data, market_context)
        
        # Run the debate
        arguments = []
        
        # 1. Aggressive (Risky) perspective
        aggressive_arg = self._get_aggressive_view(llm, symbol, position_context)
        arguments.append(aggressive_arg)
        
        # 2. Conservative (Safe) perspective  
        conservative_arg = self._get_conservative_view(llm, symbol, position_context)
        arguments.append(conservative_arg)
        
        # 3. Neutral (Balanced) perspective
        neutral_arg = self._get_neutral_view(llm, symbol, position_context, 
                                             aggressive_arg, conservative_arg)
        arguments.append(neutral_arg)
        
        # 4. Judge makes final decision
        final_decision = self._judge_debate(
            llm, symbol, position_context, arguments
        )
        
        return RiskDebateResult(
            symbol=symbol,
            arguments=arguments,
            final_decision=final_decision["action"],
            final_reasoning=final_decision["reasoning"],
            risk_score=final_decision["risk_score"],
            debate_summary=final_decision["summary"],
            timestamp=datetime.now()
        )
    
    def _prepare_position_context(
        self, 
        position_data: Dict[str, Any],
        market_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Prepare context string for the debate"""
        context = f"""
CURRENT POSITION:
- Entry Price: ${position_data.get('entry_price', 0):.2f}
- Current Price: ${position_data.get('current_price', 0):.2f}
- Quantity: {position_data.get('quantity', 0)}
- Market Value: ${position_data.get('market_value', 0):.2f}
- Unrealized P&L: ${position_data.get('unrealized_pnl', 0):.2f} ({position_data.get('unrealized_pnl_pct', 0):.1f}%)
- Days Held: {position_data.get('days_held', 0)}
- Portfolio Concentration: {position_data.get('concentration', 0):.1f}%
"""
        
        if market_context:
            context += f"""
MARKET CONTEXT:
- Market Trend: {market_context.get('trend', 'unknown')}
- Volatility: {market_context.get('volatility', 'moderate')}
- Sector Performance: {market_context.get('sector_performance', 'neutral')}
- News Sentiment: {market_context.get('news_sentiment', 'neutral')}
"""
        
        return context
    
    def _get_aggressive_view(
        self, 
        llm, 
        symbol: str, 
        position_context: str
    ) -> DebateArgument:
        """Get aggressive/risky perspective on the position"""
        prompt = f"""As an AGGRESSIVE Risk Analyst, evaluate this {symbol} position.
Your role is to champion high-reward opportunities and bold strategies.

{position_context}

Evaluate whether to: HOLD (keep full position), REDUCE (partial exit), EXIT (full exit), or ADD (increase position).

Focus on:
- Upside potential and growth opportunities
- Why caution might miss critical gains
- Bold moves that could outperform

Respond in this format:
ACTION: [HOLD/REDUCE/EXIT/ADD]
CONFIDENCE: [0.0-1.0]
REASONING: [Your aggressive case]
KEY_POINTS:
- Point 1
- Point 2
- Point 3"""

        response = llm.invoke(prompt)
        return self._parse_debate_response(response.content, DebaterStance.AGGRESSIVE)
    
    def _get_conservative_view(
        self, 
        llm, 
        symbol: str, 
        position_context: str
    ) -> DebateArgument:
        """Get conservative/safe perspective on the position"""
        prompt = f"""As a CONSERVATIVE Risk Analyst, evaluate this {symbol} position.
Your role is to prioritize capital preservation and risk management.

{position_context}

Evaluate whether to: HOLD (keep full position), REDUCE (partial exit), EXIT (full exit), or ADD (increase position).

Focus on:
- Downside risks and potential losses
- Why the current position might be overexposed
- Protecting gains and limiting losses

Respond in this format:
ACTION: [HOLD/REDUCE/EXIT/ADD]
CONFIDENCE: [0.0-1.0]
REASONING: [Your conservative case]
KEY_POINTS:
- Point 1
- Point 2
- Point 3"""

        response = llm.invoke(prompt)
        return self._parse_debate_response(response.content, DebaterStance.CONSERVATIVE)
    
    def _get_neutral_view(
        self, 
        llm, 
        symbol: str, 
        position_context: str,
        aggressive_arg: DebateArgument,
        conservative_arg: DebateArgument
    ) -> DebateArgument:
        """Get neutral/balanced perspective considering both sides"""
        prompt = f"""As a NEUTRAL Risk Analyst, evaluate this {symbol} position.
Your role is to find the balanced approach between risk and reward.

{position_context}

AGGRESSIVE VIEW: {aggressive_arg.reasoning}
CONSERVATIVE VIEW: {conservative_arg.reasoning}

Evaluate whether to: HOLD (keep full position), REDUCE (partial exit), EXIT (full exit), or ADD (increase position).

Focus on:
- Balancing the aggressive and conservative views
- Risk-adjusted returns
- Practical middle-ground recommendations

Respond in this format:
ACTION: [HOLD/REDUCE/EXIT/ADD]
CONFIDENCE: [0.0-1.0]
REASONING: [Your balanced case]
KEY_POINTS:
- Point 1
- Point 2
- Point 3"""

        response = llm.invoke(prompt)
        return self._parse_debate_response(response.content, DebaterStance.NEUTRAL)
    
    def _judge_debate(
        self,
        llm,
        symbol: str,
        position_context: str,
        arguments: List[DebateArgument]
    ) -> Dict[str, Any]:
        """Risk Manager judges the debate and makes final decision"""
        
        debate_history = "\n\n".join([
            f"**{arg.stance.value.upper()} VIEW:**\nAction: {arg.position_action}\n{arg.reasoning}"
            for arg in arguments
        ])
        
        prompt = f"""As the Risk Management Judge, evaluate this debate about {symbol} position.

{position_context}

DEBATE HISTORY:
{debate_history}

Your task:
1. Evaluate the strongest points from each perspective
2. Make a final decision: HOLD, REDUCE, EXIT, or ADD
3. Provide clear reasoning
4. Assign a risk score (0-100, higher = more risky to hold)

Respond in this format:
FINAL_ACTION: [HOLD/REDUCE/EXIT/ADD]
RISK_SCORE: [0-100]
REASONING: [Your final reasoning integrating all perspectives]
SUMMARY: [One paragraph summary of the debate and decision]"""

        response = llm.invoke(prompt)
        content = response.content
        
        # Parse response
        action = "hold"
        risk_score = 50
        reasoning = content
        summary = content
        
        lines = content.split('\n')
        for line in lines:
            line_upper = line.upper()
            if 'FINAL_ACTION:' in line_upper:
                action_text = line.split(':', 1)[1].strip().lower()
                if 'exit' in action_text:
                    action = 'exit'
                elif 'reduce' in action_text:
                    action = 'reduce'
                elif 'add' in action_text:
                    action = 'add'
                else:
                    action = 'hold'
            elif 'RISK_SCORE:' in line_upper:
                try:
                    risk_score = float(line.split(':', 1)[1].strip())
                except:
                    risk_score = 50
            elif 'REASONING:' in line_upper:
                reasoning = line.split(':', 1)[1].strip()
            elif 'SUMMARY:' in line_upper:
                summary = line.split(':', 1)[1].strip()
        
        return {
            "action": action,
            "risk_score": risk_score,
            "reasoning": reasoning,
            "summary": summary
        }
    
    def _parse_debate_response(
        self, 
        content: str, 
        stance: DebaterStance
    ) -> DebateArgument:
        """Parse LLM response into DebateArgument"""
        action = "hold"
        confidence = 0.7
        reasoning = content
        key_points = []
        
        lines = content.split('\n')
        in_key_points = False
        
        for line in lines:
            line_upper = line.upper()
            if 'ACTION:' in line_upper:
                action_text = line.split(':', 1)[1].strip().lower()
                if 'exit' in action_text:
                    action = 'exit'
                elif 'reduce' in action_text:
                    action = 'reduce'
                elif 'add' in action_text:
                    action = 'add'
                else:
                    action = 'hold'
            elif 'CONFIDENCE:' in line_upper:
                try:
                    confidence = float(line.split(':', 1)[1].strip())
                except:
                    confidence = 0.7
            elif 'REASONING:' in line_upper:
                reasoning = line.split(':', 1)[1].strip()
            elif 'KEY_POINTS:' in line_upper:
                in_key_points = True
            elif in_key_points and line.strip().startswith('-'):
                key_points.append(line.strip()[1:].strip())
        
        return DebateArgument(
            stance=stance,
            position_action=action,
            reasoning=reasoning,
            confidence=confidence,
            key_points=key_points[:5]  # Limit to 5 points
        )
    
    def get_portfolio_recommendations(
        self,
        positions: List[Dict[str, Any]],
        market_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get AI recommendations for entire portfolio.
        
        This implements: "Manage multiple positions together to balance risk"
        """
        results = []
        total_risk_score = 0
        
        for position in positions:
            symbol = position.get("symbol", "UNKNOWN")
            try:
                debate_result = self.analyze_position_with_debate(
                    symbol, position, market_context
                )
                results.append({
                    "symbol": symbol,
                    "action": debate_result.final_decision,
                    "reasoning": debate_result.final_reasoning,
                    "risk_score": debate_result.risk_score,
                    "debate_summary": debate_result.debate_summary,
                    "arguments": [
                        {
                            "stance": arg.stance.value,
                            "action": arg.position_action,
                            "confidence": arg.confidence,
                            "key_points": arg.key_points
                        }
                        for arg in debate_result.arguments
                    ]
                })
                total_risk_score += debate_result.risk_score
            except Exception as e:
                results.append({
                    "symbol": symbol,
                    "action": "hold",
                    "reasoning": f"Error analyzing: {str(e)}",
                    "risk_score": 50,
                    "error": str(e)
                })
                total_risk_score += 50
        
        # Calculate portfolio-level metrics
        avg_risk_score = total_risk_score / len(positions) if positions else 0
        
        return {
            "portfolio_risk_score": avg_risk_score,
            "portfolio_risk_level": self._risk_score_to_level(avg_risk_score),
            "positions_to_exit": [r for r in results if r["action"] == "exit"],
            "positions_to_reduce": [r for r in results if r["action"] == "reduce"],
            "positions_to_add": [r for r in results if r["action"] == "add"],
            "positions_to_hold": [r for r in results if r["action"] == "hold"],
            "all_recommendations": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _risk_score_to_level(self, score: float) -> str:
        """Convert risk score to risk level"""
        if score >= 75:
            return "critical"
        elif score >= 50:
            return "high"
        elif score >= 25:
            return "moderate"
        else:
            return "low"
