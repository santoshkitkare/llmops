from dataclasses import dataclass, field
from typing import List, Optional
import datetime

@dataclass
class Child:
    """Represents a child with their education and marriage details."""
    current_age: int
    school_fee: float
    school_fee_increase: float  # as decimal (e.g., 0.1 for 10%)
    fee_increase_frequency: int  # years between fee increases
    graduation_fee: float
    marriage_cost: float
    marriage_age: int

@dataclass
class RetirementParams:
    """Parameters for retirement planning calculations."""
    current_age: int
    retirement_age: int
    life_expectancy: int
    current_corpus: float
    pre_ret_return: float  # as decimal
    post_ret_return: float  # as decimal
    inflation: float  # as decimal
    monthly_expenses: float
    children: List[Child] = field(default_factory=list)

@dataclass
class YearlyProjection:
    """Holds the financial projection for a single year."""
    year: int
    age: int
    corpus_start: float
    household_expense: float
    school_fees: float = 0.0
    graduation_fees: float = 0.0
    marriage_expense: float = 0.0
    
    @property
    def total_withdrawals(self) -> float:
        return self.household_expense + self.school_fees + self.graduation_fees + self.marriage_expense
    
    def corpus_end(self, return_rate: float) -> float:
        """Calculate corpus at the end of the year after returns and withdrawals."""
        return (self.corpus_start * (1 + return_rate)) - self.total_withdrawals
