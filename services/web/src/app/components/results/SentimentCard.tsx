import { Stack, Group, Text, Divider, Badge } from "@mantine/core";
import type {
  SentimentResult,
  SentimentAssessment,
  Allegation,
  ToneSignals,
} from "~/types/screening";
import { ExpandableCard } from "../shared/ExpandableCard";
import { StatusBadge } from "../shared/StatusBadge";
import { getRiskColor, getRiskLabel } from "~/lib/screening-utils";

interface SentimentCardProps {
  sentiment: SentimentResult | null;
  isExpanded: boolean;
  onToggle: () => void;
}

// Config for tone signals to display
type ToneSignalConfig = {
  key: keyof ToneSignals;
  label: string;
  nullable?: boolean;
  isBoolean?: boolean;
};

const TONE_SIGNALS_CONFIG: ToneSignalConfig[] = [
  { key: "certainty_level", label: "Certainty" },
  { key: "attribution_quality", label: "Attribution" },
  { key: "temporal_context", label: "Temporal", nullable: true },
  { key: "hedging_language", label: "Hedging", isBoolean: true },
  { key: "subject_denial", label: "Subject Denial", isBoolean: true },
];

// Sub-component: Allegation evidence display
function AllegationEvidence({ allegation }: { allegation: Allegation }) {
  if (allegation.evidence_spans.length === 0) return null;

  return (
    <div
      style={{
        background: "#f8f9fa",
        padding: "8px",
        borderRadius: "4px",
        marginTop: "8px",
      }}
    >
      <Text size="xs" c="dimmed" mb="xs">
        Evidence:
      </Text>
      {allegation.evidence_spans.map((span, spanIdx) => (
        <Text key={spanIdx} size="xs" style={{ fontStyle: "italic" }}>
          {`"${span.quote}"`}
        </Text>
      ))}
    </div>
  );
}

// Sub-component: Allegation metadata (amount, timeframe, jurisdiction)
function AllegationMetadata({ allegation }: { allegation: Allegation }) {
  const hasMetadata =
    allegation.monetary_amount ??
    allegation.timeframe ??
    allegation.jurisdiction;

  if (!hasMetadata) return null;

  const metadataItems = [
    { label: "Amount", value: allegation.monetary_amount },
    { label: "When", value: allegation.timeframe },
    { label: "Where", value: allegation.jurisdiction },
  ];

  return (
    <Group gap="md" mt="xs">
      {metadataItems.map(
        (item, idx) =>
          item.value && (
            <Text key={idx} size="xs" c="dimmed">
              {item.label}: {item.value}
            </Text>
          ),
      )}
    </Group>
  );
}

// Sub-component: Individual allegation card
function AllegationCard({ allegation }: { allegation: Allegation }) {
  return (
    <div
      style={{
        padding: "12px",
        border: "1px solid #dee2e6",
        borderRadius: "8px",
      }}
    >
      <Group justify="space-between" mb="xs">
        <Badge color="red" variant="light">
          {allegation.category.replace(/_/g, " ")}
        </Badge>
        <Group gap="xs">
          <Badge size="sm" variant="outline">
            {allegation.severity}
          </Badge>
          <Badge size="sm" variant="outline">
            {allegation.status}
          </Badge>
        </Group>
      </Group>
      <Text size="sm" mb="xs">
        {allegation.description}
      </Text>
      <AllegationEvidence allegation={allegation} />
      {allegation.subject_response && (
        <div style={{ marginTop: "8px" }}>
          <Text size="xs" fw={500} c="dimmed">
            Subject Response:
          </Text>
          <Text size="xs">{allegation.subject_response}</Text>
        </div>
      )}
      <AllegationMetadata allegation={allegation} />
    </div>
  );
}

// Sub-component: Tone signals display
function ToneSignalsDisplay({ toneSignals }: { toneSignals: ToneSignals }) {
  return (
    <div>
      <Text size="sm" fw={500} mb="xs">
        Tone & Context
      </Text>
      <Group gap="md">
        {TONE_SIGNALS_CONFIG.map((config) => {
          const value = toneSignals[config.key];
          let displayValue: string;

          if (config.isBoolean) {
            displayValue = value ? "Yes" : "No";
          } else if (config.nullable && !value) {
            displayValue = "N/A";
          } else {
            displayValue = String(value);
          }

          return (
            <div key={config.key}>
              <Text size="xs" c="dimmed">
                {config.label}
              </Text>
              <Text size="sm">{displayValue}</Text>
            </div>
          );
        })}
      </Group>
    </div>
  );
}

// Sub-component: Related entities section
function RelatedEntitiesSection({ entities }: { entities: string[] }) {
  if (entities.length === 0) return null;

  return (
    <>
      <Divider />
      <div>
        <Text size="sm" fw={500} mb="xs">
          Related Entities with Adverse Content
        </Text>
        <Group gap="xs">
          {entities.map((entity, idx) => (
            <Badge key={idx} variant="light">
              {entity}
            </Badge>
          ))}
        </Group>
      </div>
    </>
  );
}

// Sub-component: Assessment summary for collapsed state
function AssessmentSummary({
  assessment,
}: {
  assessment: SentimentAssessment;
}) {
  return (
    <Stack gap="xs">
      <Group gap="xs">
        <Text size="sm" fw={500}>
          {assessment.allegations.length} Allegation
          {assessment.allegations.length !== 1 ? "s" : ""} Found
        </Text>
        {assessment.requires_manual_review && (
          <Badge color="orange" variant="light" size="sm">
            🔍 Manual Review Required
          </Badge>
        )}
      </Group>
      {assessment.allegations.slice(0, 3).map((allegation, idx) => (
        <Group key={idx} gap="xs">
          <Badge size="sm" color="red" variant="dot">
            {allegation.category.replace(/_/g, " ")}
          </Badge>
          <Text size="xs" c="dimmed">
            ({allegation.severity} severity, {allegation.status})
          </Text>
        </Group>
      ))}
      <Text size="sm" c="dimmed" mt="xs">
        {assessment.rationale}
      </Text>
    </Stack>
  );
}

// Sub-component: Full assessment details (expanded view)
function AssessmentDetails({
  assessment,
}: {
  assessment: SentimentAssessment;
}) {
  return (
    <Stack gap="lg">
      <div>
        <Text size="sm" fw={500} mb="md">
          Allegations ({assessment.allegations.length})
        </Text>
        <Stack gap="md">
          {assessment.allegations.map((allegation, idx) => (
            <AllegationCard key={idx} allegation={allegation} />
          ))}
        </Stack>
      </div>

      <Divider />

      <ToneSignalsDisplay toneSignals={assessment.tone_signals} />

      <Divider />

      <div>
        <Text size="sm" fw={500} mb="xs">
          Analysis Rationale
        </Text>
        <Text size="sm">{assessment.rationale}</Text>
      </div>

      <RelatedEntitiesSection
        entities={assessment.related_entities_mentioned}
      />
    </Stack>
  );
}

// Main component
export function SentimentCard({
  sentiment,
  isExpanded,
  onToggle,
}: SentimentCardProps) {
  if (!sentiment || sentiment.assessments.length === 0) {
    return (
      <ExpandableCard
        title="⚖️ Adverse Media Assessment"
        badge={<StatusBadge label="No Adverse Content" color="green" />}
        isExpanded={isExpanded}
        onToggle={onToggle}
        defaultContent={
          <Text size="sm" c="dimmed">
            No adverse media content detected for the matched person.
          </Text>
        }
      >
        <Text size="sm" c="dimmed">
          The article does not contain adverse allegations or risk indicators.
        </Text>
      </ExpandableCard>
    );
  }

  const assessment = sentiment.assessments[0]; // Primary assessment
  if (!assessment) return null;

  return (
    <ExpandableCard
      title="⚖️ Adverse Media Assessment"
      badge={
        <Group gap="xs">
          <StatusBadge
            label={getRiskLabel(assessment.risk_category)}
            color={getRiskColor(assessment.risk_category)}
          />
          <StatusBadge
            label={`Risk: ${assessment.risk_score.toFixed(2)}`}
            color={getRiskColor(assessment.risk_category)}
            variant="outline"
          />
        </Group>
      }
      isExpanded={isExpanded}
      onToggle={onToggle}
      defaultContent={<AssessmentSummary assessment={assessment} />}
    >
      <AssessmentDetails assessment={assessment} />
    </ExpandableCard>
  );
}
