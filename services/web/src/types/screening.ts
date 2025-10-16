// TypeScript interfaces matching Python Pydantic models
// This manual mapping is unfortunate but OK for an MVP.

export interface AnalyserMetadata {
  processed_at: string;
  processing_time_seconds: number | null;
  llm_provider: string | null;
  llm_model: string | null;
  analyser_version: string | null;
  prompt_version: string | null;
}

// Article
export interface Article {
  url: string;
  title: string;
  content: string;
}

// Query Person
export interface QueryPerson {
  name: string;
  date_of_birth: string | null;
  normalised_name: string;
  possible_nicknames: string[];
  birth_year: number | null;
}

// Credibility
export type SignalValue = "yes" | "no" | "unsure";

export interface CredibilitySignals {
  has_attribution: SignalValue;
  has_multiple_sources: SignalValue;
  distinguishes_fact_allegation: SignalValue;
  has_named_quotes: SignalValue;
  has_balanced_coverage: SignalValue;
  is_internally_consistent: SignalValue;
  has_technical_detail: SignalValue;
  uses_hedging_language: SignalValue;
  has_sensational_language: SignalValue;
  has_excessive_anonymous_sources: SignalValue;
  lacks_substantiating_detail: SignalValue;
  has_poor_grammar: SignalValue;
  has_conspiratorial_framing: SignalValue;
  has_vague_institutions: SignalValue;
  has_meta_claims: SignalValue;
  has_emotional_tone: SignalValue;
}

export type CredibilityRecommendation =
  | "reliable"
  | "questionable"
  | "unreliable";

export interface CredibilityAssessment {
  signals: CredibilitySignals;
  credibility_score: number;
  recommendation: CredibilityRecommendation;
  rationale: string;
  key_strengths: string[];
  key_weaknesses: string[];
  hard_red_flags: string[];
}

export interface CredibilityResult {
  assessment: CredibilityAssessment;
  metadata: AnalyserMetadata;
}

// Entity Extraction
export interface Employment {
  role: string;
  organization: string | null;
  location: string | null;
  timeframe: string | null;
  evidence_quote: string;
}

export interface Relationship {
  related_entity_name: string;
  relationship_type: string;
  description: string;
  evidence_quote: string;
}

export interface Entity {
  id: string;
  name: string;
  aliases: string[];
  age: number | null;
  birth_year: number | null;
  date_of_birth: string | null;
  employments: Employment[];
  locations: string[];
  nationalities: string[];
  place_of_birth: string | null;
  identifiers: string[];
  relationships: Relationship[];
  mention_sentences: string[];
  mention_count: number;
  extraction_confidence: number;
}

export interface ExtractionResult {
  entities: Entity[];
  metadata: AnalyserMetadata;
}

// Matching
export type MatchDecision =
  | "definite_match"
  | "probable_match"
  | "possible_match"
  | "uncertain"
  | "no_match";

export type SignalMatch = "match" | "no_match" | "unknown";

export interface NameSignals {
  exact_match: SignalMatch;
  fuzzy_similarity: number;
  nickname_match: SignalMatch;
  partial_match: SignalMatch;
  title_stripped_match: SignalMatch;
}

export interface DemographicSignals {
  dob_exact_match: SignalMatch;
  birth_year_match: SignalMatch;
  age_discrepancy_years: number | null;
}

export interface MatchSignals {
  name: NameSignals;
  demographics: DemographicSignals;
}

export interface PersonMatch {
  entity_id: string;
  entity_name: string;
  decision: MatchDecision;
  confidence: number;
  signals: MatchSignals;
  reasoning: string;
  evidence_for_match: string[];
  evidence_against_match: string[];
  is_primary_match: boolean;
}

export interface MatchingResult {
  query_person: QueryPerson;
  entities_analysed: string[];
  matches: PersonMatch[];
  has_definite_match: boolean;
  has_any_match: boolean;
  requires_manual_review: boolean;
  primary_match: PersonMatch | null;
  summary: string;
  metadata: AnalyserMetadata;
}

// Sentiment Analysis
export type AllegationCategory =
  | "criminal"
  | "money_laundering"
  | "corruption"
  | "fraud"
  | "regulatory_violation"
  | "litigation"
  | "sanctions"
  | "investigation"
  | "scandal"
  | "conflict_of_interest"
  | "abuse_of_power"
  | "human_rights"
  | "environmental"
  | "terrorism"
  | "smuggling"
  | "ip_theft"
  | "cybercrime"
  | "negligence"
  | "bankruptcy"
  | "reputational_damage"
  | "ethical_violation";

export type AllegationStatus =
  | "alleged"
  | "investigated"
  | "charged"
  | "convicted"
  | "acquitted"
  | "dismissed";

export type AllegationSeverity = "low" | "medium" | "high" | "critical";

export interface EvidenceSpan {
  quote: string;
  start_index: number | null;
  end_index: number | null;
}

export interface Allegation {
  category: AllegationCategory;
  description: string;
  status: AllegationStatus;
  severity: AllegationSeverity;
  monetary_amount: string | null;
  timeframe: string | null;
  jurisdiction: string | null;
  evidence_spans: EvidenceSpan[];
  subject_response: string | null;
}

export type CertaintyLevel =
  | "definite"
  | "probable"
  | "alleged"
  | "speculative";
export type AttributionQuality =
  | "named_sources"
  | "anonymous_sources"
  | "no_attribution";
export type TemporalContext = "recent" | "ongoing" | "historical" | null;

export interface ToneSignals {
  certainty_level: CertaintyLevel;
  hedging_language: boolean;
  attribution_quality: AttributionQuality;
  temporal_context: TemporalContext;
  subject_denial: boolean;
  contradictory_evidence: boolean;
}

export type SentimentPolarity = "adverse" | "neutral" | "positive";
export type RiskCategory =
  | "high_risk"
  | "medium_risk"
  | "low_risk"
  | "no_adverse_content";

export interface SentimentAssessment {
  entity_id: string;
  entity_name: string;
  allegations: Allegation[];
  tone_signals: ToneSignals;
  overall_polarity: SentimentPolarity;
  risk_score: number;
  risk_category: RiskCategory;
  related_entities_mentioned: string[];
  rationale: string;
  requires_manual_review: boolean;
}

export interface SentimentResult {
  assessments: SentimentAssessment[];
  metadata: AnalyserMetadata;
}

// Main Screening Result
export interface ScreeningResult {
  article: Article;
  article_credibility: CredibilityResult | null;
  query_person: QueryPerson;
  entities: Entity[];
  matching: MatchingResult;
  sentiment: SentimentResult | null;
}
