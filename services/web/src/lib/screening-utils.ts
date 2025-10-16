import type {
  MatchDecision,
  RiskCategory,
  CredibilityRecommendation,
} from "~/types/screening";

export type MantineColor =
  | "green"
  | "yellow"
  | "orange"
  | "red"
  | "gray"
  | "blue"
  | "teal"
  | "cyan";

// Match decision mappings
const MATCH_COLORS: Record<MatchDecision, MantineColor> = {
  definite_match: "green",
  probable_match: "teal",
  possible_match: "yellow",
  uncertain: "orange",
  no_match: "gray",
};

const MATCH_LABELS: Record<MatchDecision, string> = {
  definite_match: "Definite Match",
  probable_match: "Probable Match",
  possible_match: "Possible Match",
  uncertain: "Uncertain",
  no_match: "No Match",
};

export const getMatchColor = (decision: MatchDecision): MantineColor =>
  MATCH_COLORS[decision];

export const getMatchLabel = (decision: MatchDecision): string =>
  MATCH_LABELS[decision];

// Risk category mappings
const RISK_COLORS: Record<RiskCategory, MantineColor> = {
  high_risk: "red",
  medium_risk: "orange",
  low_risk: "yellow",
  no_adverse_content: "green",
};

const RISK_LABELS: Record<RiskCategory, string> = {
  high_risk: "High Risk",
  medium_risk: "Medium Risk",
  low_risk: "Low Risk",
  no_adverse_content: "No Adverse Content",
};

export const getRiskColor = (category: RiskCategory): MantineColor =>
  RISK_COLORS[category];

export const getRiskLabel = (category: RiskCategory): string =>
  RISK_LABELS[category];

// Credibility mappings
const CREDIBILITY_COLORS: Record<CredibilityRecommendation, MantineColor> = {
  reliable: "green",
  questionable: "yellow",
  unreliable: "red",
};

const CREDIBILITY_LABELS: Record<CredibilityRecommendation, string> = {
  reliable: "Reliable",
  questionable: "Questionable",
  unreliable: "Unreliable",
};

export const getCredibilityColor = (
  recommendation: CredibilityRecommendation,
): MantineColor => CREDIBILITY_COLORS[recommendation];

export const getCredibilityLabel = (
  recommendation: CredibilityRecommendation,
): string => CREDIBILITY_LABELS[recommendation];

// Formatters
export const formatConfidence = (confidence: number): string =>
  `${Math.round(confidence * 100)}%`;

export const formatScore = (score: number): string => score.toFixed(2);
