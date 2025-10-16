import { Stack, Group, Text, Divider, Grid } from "@mantine/core";
import type {
  MatchingResult,
  NameSignals,
  PersonMatch,
} from "~/types/screening";
import { ExpandableCard } from "../shared/ExpandableCard";
import { StatusBadge } from "../shared/StatusBadge";
import { EvidenceList } from "../shared/EvidenceList";
import {
  getMatchColor,
  getMatchLabel,
  formatConfidence,
} from "~/lib/screening-utils";

interface MatchCardProps {
  matching: MatchingResult;
  isExpanded: boolean;
  onToggle: () => void;
}

type MatchSignalConfig = {
  key: keyof NameSignals;
  label: string;
  formatter: (value: string | number) => string;
};

const MATCH_SIGNALS_CONFIG: MatchSignalConfig[] = [
  {
    key: "exact_match",
    label: "Exact Match",
    formatter: (value) => String(value),
  },
  {
    key: "fuzzy_similarity",
    label: "Fuzzy Similarity",
    formatter: (value) => formatConfidence(Number(value)),
  },
  {
    key: "partial_match",
    label: "Partial Match",
    formatter: (value) => String(value),
  },
  {
    key: "nickname_match",
    label: "Nickname Match",
    formatter: (value) => String(value),
  },
];

// Sub-component: Match summary for collapsed state
function MatchSummary({
  match,
  queryName,
}: {
  match: PersonMatch;
  queryName: string;
}) {
  return (
    <Stack gap="xs">
      <Text size="sm">
        <Text span fw={500}>
          Query:
        </Text>{" "}
        {queryName}
      </Text>
      {match.entity_name !== queryName && (
        <Text size="sm">
          <Text span fw={500}>
            Article mentions:
          </Text>{" "}
          {match.entity_name}
        </Text>
      )}
      <Text size="sm" c="dimmed">
        {match.reasoning}
      </Text>
    </Stack>
  );
}

// Sub-component: Match signals grid
function MatchSignalsGrid({ match }: { match: PersonMatch }) {
  return (
    <div>
      <Text size="sm" fw={500} mb="xs">
        Match Signals
      </Text>
      <Grid>
        {MATCH_SIGNALS_CONFIG.map((signal) => {
          const value = match.signals.name[signal.key];
          return (
            <Grid.Col key={signal.key} span={6}>
              <Text size="sm" c="dimmed">
                {signal.label}
              </Text>
              <Text size="sm">{signal.formatter(value)}</Text>
            </Grid.Col>
          );
        })}
      </Grid>
    </div>
  );
}

// Sub-component: Match details (expanded view)
function MatchDetails({ match }: { match: PersonMatch }) {
  return (
    <Stack gap="lg">
      <MatchSignalsGrid match={match} />
      <Divider />
      <EvidenceList
        title="Evidence Supporting Match:"
        items={match.evidence_for_match}
        color="green"
      />
      {match.evidence_against_match.length > 0 && (
        <EvidenceList
          title="Evidence Against Match:"
          items={match.evidence_against_match}
          color="red"
        />
      )}
      <div>
        <Text size="sm" fw={500} mb="xs">
          Full Reasoning
        </Text>
        <Text size="sm">{match.reasoning}</Text>
      </div>
    </Stack>
  );
}

// Main component
export function MatchCard({ matching, isExpanded, onToggle }: MatchCardProps) {
  const primaryMatch = matching.primary_match;

  const renderBadge = () => {
    if (!primaryMatch) {
      return <StatusBadge label="No Match" color="gray" />;
    }
    return (
      <Group gap="xs">
        <StatusBadge
          label={getMatchLabel(primaryMatch.decision)}
          color={getMatchColor(primaryMatch.decision)}
        />
        <StatusBadge
          label={formatConfidence(primaryMatch.confidence)}
          color={getMatchColor(primaryMatch.decision)}
          variant="outline"
        />
      </Group>
    );
  };

  const renderDefaultContent = () => {
    if (!primaryMatch) {
      return (
        <Text size="sm" c="dimmed">
          {matching.summary}
        </Text>
      );
    }
    return (
      <MatchSummary
        match={primaryMatch}
        queryName={matching.query_person.name}
      />
    );
  };

  const renderExpandedContent = () => {
    if (!primaryMatch) {
      return (
        <Text size="sm" c="dimmed">
          No matching person found in the article. Analysed{" "}
          {matching.entities_analysed.length} entities.
        </Text>
      );
    }
    return <MatchDetails match={primaryMatch} />;
  };

  return (
    <ExpandableCard
      title="👤 Person Match"
      badge={renderBadge()}
      isExpanded={isExpanded}
      onToggle={onToggle}
      defaultContent={renderDefaultContent()}
    >
      {renderExpandedContent()}
    </ExpandableCard>
  );
}
