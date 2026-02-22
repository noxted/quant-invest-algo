"""
Portfolio Profile Configurations
Defines risk profiles (Conservative, Intermediate, Aggressive) with asset class and sector weights
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class PortfolioProfile:
    """Portfolio allocation profile with risk weights and constraints"""
    name: str
    risk_level: int  # 1-3 (Conservative, Intermediate, Aggressive)
    
    # MEGA LAYER: Asset Class Allocation (Fixed Income, FIIs, Brazilian Stocks, US Stocks)
    fixed_income_pct: float  # Fixed income range
    fixed_income_min: float
    fixed_income_max: float
    
    fiis_pct: float  # FIIs range
    fiis_min: float
    fiis_max: float
    
    br_stocks_pct: float  # Brazilian stocks range
    br_stocks_min: float
    br_stocks_max: float
    
    us_stocks_pct: float  # US stocks range
    us_stocks_min: float
    us_stocks_max: float
    
    # MESO LAYER: Sector Allocation weights (base allocation)
    sector_weights: Dict[str, float]  # Energy, Real Estate, Agriculture, Tech, IA, Finance, etc.
    sector_min: Dict[str, float]  # Minimum allocation per sector
    sector_max: Dict[str, float]  # Maximum allocation per sector
    
    # Risk Management Parameters
    max_drawdown_tolerance: float  # Maximum acceptable drawdown
    max_single_position: float  # Max % in single stock
    rebalance_threshold: float  # When to rebalance (e.g., 0.05 = 5% drift)
    
    # RL Training Parameters
    reward_metric: str  # Sharpe, Sortino, Calmar
    risk_penalty_factor: float  # How much to penalize risk


# CONSERVATIVE PROFILE (Low Risk, Capital Preservation)
CONSERVATIVE = PortfolioProfile(
    name="Conservative",
    risk_level=1,
    
    # MEGA LAYER
    fixed_income_pct=0.50, fixed_income_min=0.40, fixed_income_max=0.60,
    fiis_pct=0.20, fiis_min=0.10, fiis_max=0.30,
    br_stocks_pct=0.20, br_stocks_min=0.10, br_stocks_max=0.30,
    us_stocks_pct=0.10, us_stocks_min=0.05, us_stocks_max=0.20,
    
    # MESO LAYER: Conservative sector allocation
    sector_weights={
        "energy": 0.15,  # Mature, dividend-yielding
        "real_estate": 0.25,  # Stable cashflow from FIIs
        "finance": 0.20,  # Banks and insurance (stable)
        "agriculture": 0.15,  # Commodity-linked, low volatility
        "healthcare": 0.15,  # Defensive
        "tech": 0.05,  # Small allocation
        "ia": 0.05,  # Minimal IA exposure
    },
    sector_min={
        "energy": 0.08, "real_estate": 0.15, "finance": 0.10,
        "agriculture": 0.08, "healthcare": 0.08, "tech": 0.02, "ia": 0.01,
    },
    sector_max={
        "energy": 0.25, "real_estate": 0.40, "finance": 0.30,
        "agriculture": 0.25, "healthcare": 0.25, "tech": 0.10, "ia": 0.08,
    },
    
    # Risk Management
    max_drawdown_tolerance=0.15,  # Max 15% drawdown
    max_single_position=0.10,  # Max 10% in single stock
    rebalance_threshold=0.05,  # Rebalance if 5% drift
    
    # RL Training
    reward_metric="Sortino",  # Downside-focused
    risk_penalty_factor=0.8,  # High penalty for losses
)


# INTERMEDIATE PROFILE (Balanced Growth and Protection)
INTERMEDIATE = PortfolioProfile(
    name="Intermediate",
    risk_level=2,
    
    # MEGA LAYER
    fixed_income_pct=0.35, fixed_income_min=0.25, fixed_income_max=0.45,
    fiis_pct=0.20, fiis_min=0.15, fiis_max=0.30,
    br_stocks_pct=0.30, br_stocks_min=0.20, br_stocks_max=0.40,
    us_stocks_pct=0.15, us_stocks_min=0.08, us_stocks_max=0.25,
    
    # MESO LAYER: Balanced sector allocation
    sector_weights={
        "energy": 0.12,
        "real_estate": 0.20,
        "finance": 0.15,
        "agriculture": 0.12,
        "healthcare": 0.12,
        "tech": 0.18,  # Increased tech exposure
        "ia": 0.11,  # Moderate IA
    },
    sector_min={
        "energy": 0.06, "real_estate": 0.12, "finance": 0.08,
        "agriculture": 0.06, "healthcare": 0.06, "tech": 0.08, "ia": 0.05,
    },
    sector_max={
        "energy": 0.20, "real_estate": 0.30, "finance": 0.25,
        "agriculture": 0.20, "healthcare": 0.20, "tech": 0.30, "ia": 0.18,
    },
    
    # Risk Management
    max_drawdown_tolerance=0.25,  # Max 25% drawdown
    max_single_position=0.12,  # Max 12% in single stock
    rebalance_threshold=0.07,  # Rebalance if 7% drift
    
    # RL Training
    reward_metric="Sharpe",  # Risk-adjusted returns
    risk_penalty_factor=0.5,  # Moderate penalty
)


# AGGRESSIVE PROFILE (Growth Focused, Higher Risk Tolerance)
AGGRESSIVE = PortfolioProfile(
    name="Aggressive",
    risk_level=3,
    
    # MEGA LAYER
    fixed_income_pct=0.15, fixed_income_min=0.08, fixed_income_max=0.25,
    fiis_pct=0.15, fiis_min=0.08, fiis_max=0.25,
    br_stocks_pct=0.40, br_stocks_min=0.30, br_stocks_max=0.50,
    us_stocks_pct=0.30, us_stocks_min=0.20, us_stocks_max=0.45,
    
    # MESO LAYER: Growth-focused sector allocation
    sector_weights={
        "energy": 0.08,
        "real_estate": 0.10,
        "finance": 0.10,
        "agriculture": 0.08,
        "healthcare": 0.09,
        "tech": 0.30,  # High tech exposure
        "ia": 0.25,  # High IA exposure for growth
    },
    sector_min={
        "energy": 0.03, "real_estate": 0.05, "finance": 0.05,
        "agriculture": 0.03, "healthcare": 0.03, "tech": 0.15, "ia": 0.12,
    },
    sector_max={
        "energy": 0.15, "real_estate": 0.20, "finance": 0.18,
        "agriculture": 0.15, "healthcare": 0.18, "tech": 0.45, "ia": 0.40,
    },
    
    # Risk Management
    max_drawdown_tolerance=0.40,  # Max 40% drawdown
    max_single_position=0.15,  # Max 15% in single stock
    rebalance_threshold=0.10,  # Rebalance if 10% drift
    
    # RL Training
    reward_metric="Calmar",  # Return/max-drawdown ratio
    risk_penalty_factor=0.2,  # Low penalty for volatility
)


# Profile Registry
PROFILES = {
    "conservative": CONSERVATIVE,
    "intermediate": INTERMEDIATE,
    "aggressive": AGGRESSIVE,
}


def get_profile(profile_name: str) -> PortfolioProfile:
    """
    Get portfolio profile by name
    
    Args:
        profile_name: "conservative", "intermediate", or "aggressive"
        
    Returns:
        PortfolioProfile instance
    """
    profile_name = profile_name.lower()
    if profile_name not in PROFILES:
        raise ValueError(f"Unknown profile: {profile_name}. Available: {list(PROFILES.keys())}")
    return PROFILES[profile_name]


def validate_profile(profile: PortfolioProfile) -> bool:
    """
    Validate that a profile's allocations sum to 100%
    
    Args:
        profile: PortfolioProfile to validate
        
    Returns:
        True if valid
    """
    mega_total = (profile.fixed_income_pct + profile.fiis_pct + 
                  profile.br_stocks_pct + profile.us_stocks_pct)
    
    if abs(mega_total - 1.0) > 0.01:  # Allow 1% tolerance
        raise ValueError(f"Profile {profile.name} mega layer doesn't sum to 100%: {mega_total:.2%}")
    
    sector_total = sum(profile.sector_weights.values())
    if abs(sector_total - 1.0) > 0.01:  # Allow 1% tolerance
        raise ValueError(f"Profile {profile.name} sectors don't sum to 100%: {sector_total:.2%}")
    
    return True


# Validate all profiles on import
for profile in PROFILES.values():
    validate_profile(profile)
