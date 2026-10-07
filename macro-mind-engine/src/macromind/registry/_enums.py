"""AUTO-GENERATED. DO NOT EDIT. Source: registries/v0_3/*.yaml."""

from enum import StrEnum


class AnalysisContext(StrEnum):
    HISTORICAL_RECONSTRUCTION = "historical_reconstruction"
    HISTORICAL_RECONSTRUCTION_AND_METHOD_OBSERVATION = "historical_reconstruction_and_method_observation"
    METHOD_OBSERVATION_AFTER_ARGUMENT_EXTRACTION = "method_observation_after_argument_extraction"
    MODEL_DIAGNOSTIC = "model_diagnostic"
    VERIFICATION_NOT_CREATOR_RECONSTRUCTION = "verification_not_creator_reconstruction"
    UNKNOWN = "unknown"

class ComparisonType(StrEnum):
    NONE = "none"
    YOY = "yoy"
    QOQ = "qoq"
    MOM = "mom"
    SEQUENTIAL = "sequential"
    VERSUS_CONSENSUS = "versus_consensus"
    VERSUS_GUIDANCE = "versus_guidance"
    VERSUS_BASELINE = "versus_baseline"
    VERSUS_PRIOR_PERIOD = "versus_prior_period"
    PERCENTAGE_POINT_CHANGE = "percentage_point_change"
    ABSOLUTE_DELTA = "absolute_delta"
    INDEXED_TO = "indexed_to"
    OTHER = "other"
    UNKNOWN = "unknown"

class ExpressionLevel(StrEnum):
    EXPLICIT = "explicit"
    STRONGLY_IMPLIED = "strongly_implied"
    MIXED_EXPLICIT_STRONGLY_IMPLIED = "mixed_explicit_strongly_implied"
    MODEL_RECONSTRUCTION = "model_reconstruction"
    UNKNOWN = "unknown"

class FailureType(StrEnum):
    DIMENSIONAL_ERROR = "dimensional_error"
    SCOPE_SHIFT = "scope_shift"
    DENOMINATOR_SHIFT = "denominator_shift"
    TEMPORAL_MISMATCH = "temporal_mismatch"
    UNSUPPORTED_CAUSAL_JUMP = "unsupported_causal_jump"
    MOTIVE_OVERREACH = "motive_overreach"
    ANALOGY_OVERREACH = "analogy_overreach"
    OBJECT_ROLE_SHIFT = "object_role_shift"
    CLOSED_EXPLANATION = "closed_explanation"
    OTHER = "other"
    UNKNOWN = "unknown"

class HeuristicStatus(StrEnum):
    CANDIDATE = "candidate"
    UNKNOWN = "unknown"

class RecognitionStage(StrEnum):
    PLANNED = "planned"
    CONTRACTED = "contracted"
    ORDERED = "ordered"
    COMMITTED = "committed"
    DELIVERED = "delivered"
    DEPLOYED = "deployed"
    UTILIZED = "utilized"
    REVENUE_RECOGNIZED = "revenue_recognized"
    CASH_COLLECTED = "cash_collected"
    EXPENSED = "expensed"
    DEPRECIATED = "depreciated"
    IMPAIRED = "impaired"
    UNKNOWN = "unknown"

class RecurrenceMatch(StrEnum):
    NONE = "none"
    EXACT = "exact"
    PARTIAL = "partial"
    ANALOGOUS = "analogous"
    UNCERTAIN = "uncertain"
    UNKNOWN = "unknown"

class RecurrenceStatus(StrEnum):
    FIRST_OBSERVATION = "first_observation"
    REPEATED = "repeated"
    FREQUENT = "frequent"
    CANDIDATE_PATTERN = "candidate_pattern"
    UNKNOWN = "unknown"

class ResolutionStatus(StrEnum):
    NOT_APPLICABLE = "not_applicable"
    NOT_EVALUATED = "not_evaluated"
    NOT_YET_EVALUATED = "not_yet_evaluated"
    PENDING_REVIEW = "pending_review"
    UNKNOWN = "unknown"

class ReviewStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"
    UNKNOWN = "unknown"

class SemanticRole(StrEnum):
    DEMAND = "demand"
    ORDER = "order"
    CONTRACT = "contract"
    BACKLOG = "backlog"
    OBLIGATION = "obligation"
    REVENUE = "revenue"
    CASH_RECEIPT = "cash_receipt"
    CAPACITY = "capacity"
    UTILIZATION = "utilization"
    ASSET = "asset"
    CAPEX = "capex"
    DEPRECIATION = "depreciation"
    IMPAIRMENT = "impairment"
    OPERATING_EXPENSE = "operating_expense"
    OPERATING_COST = "operating_cost"
    CASH_FLOW = "cash_flow"
    PROFIT = "profit"
    MARGIN = "margin"
    VALUATION = "valuation"
    PRICE = "price"
    VOLUME = "volume"
    INVENTORY = "inventory"
    OTHER = "other"
    UNKNOWN = "unknown"

class SignalType(StrEnum):
    ANALOGY_PATTERN = "analogy_pattern"
    ATTENTION_PATTERN = "attention_pattern"
    BRANCHING_PATTERN = "branching_pattern"
    EVIDENCE_PREFERENCE = "evidence_preference"
    FAILURE_PATTERN = "failure_pattern"
    JUDGMENT_PATTERN = "judgment_pattern"
    MECHANISM_USAGE = "mechanism_usage"
    QUESTION_PATTERN = "question_pattern"
    UNKNOWN = "unknown"

class Transferability(StrEnum):
    ANALYST_SPECIFIC = "analyst_specific"
    DOMAIN_SPECIFIC = "domain_specific"
    POTENTIALLY_GENERAL = "potentially_general"
    UNKNOWN = "unknown"

class ValueKind(StrEnum):
    TARGET = "target"
    DESIGN_CAPACITY = "design_capacity"
    GUIDANCE = "guidance"
    OBSERVED_VALUE = "observed_value"
    UNKNOWN = "unknown"

class VerificationStatus(StrEnum):
    VERIFIED = "verified"
    LIKELY_TRUE = "likely_true"
    UNCERTAIN = "uncertain"
    DISPUTED = "disputed"
    LIKELY_FALSE = "likely_false"
    FALSE = "false"
    UNVERIFIABLE = "unverifiable"
    UNKNOWN = "unknown"


ENUM_TYPES = {
    "AnalysisContext": AnalysisContext,
    "ComparisonType": ComparisonType,
    "ExpressionLevel": ExpressionLevel,
    "FailureType": FailureType,
    "HeuristicStatus": HeuristicStatus,
    "RecognitionStage": RecognitionStage,
    "RecurrenceMatch": RecurrenceMatch,
    "RecurrenceStatus": RecurrenceStatus,
    "ResolutionStatus": ResolutionStatus,
    "ReviewStatus": ReviewStatus,
    "SemanticRole": SemanticRole,
    "SignalType": SignalType,
    "Transferability": Transferability,
    "ValueKind": ValueKind,
    "VerificationStatus": VerificationStatus,
}
