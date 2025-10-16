import { Stack, Button, Group, Modal, Code } from "@mantine/core";
import type { ScreeningResult } from "~/types/screening";
import { useScreeningResult } from "../hooks/useScreeningResult";
import { ArticleHeader } from "./results/ArticleHeader";
import { MatchCard } from "./results/MatchCard";
import { SentimentCard } from "./results/SentimentCard";

interface ScreeningResultDisplayProps {
  result: ScreeningResult;
  onNewSearch: () => void;
}

export function ScreeningResultDisplay({
  result,
  onNewSearch,
}: ScreeningResultDisplayProps) {
  const {
    showRawJson,
    setShowRawJson,
    isSectionExpanded,
    toggleSection,
    expandAll,
    collapseAll,
  } = useScreeningResult();

  return (
    <>
      <Stack gap="lg">
        <Group justify="space-between">
          <Group gap="sm">
            <Button onClick={onNewSearch} variant="default">
              New Search
            </Button>
            <Button onClick={() => setShowRawJson(true)} variant="subtle">
              View Raw JSON
            </Button>
          </Group>
          <Group gap="sm">
            <Button onClick={expandAll} size="compact-sm" variant="subtle">
              Expand All
            </Button>
            <Button onClick={collapseAll} size="compact-sm" variant="subtle">
              Collapse All
            </Button>
          </Group>
        </Group>

        <ArticleHeader
          article={result.article}
          credibility={result.article_credibility}
        />

        <MatchCard
          matching={result.matching}
          isExpanded={isSectionExpanded("match")}
          onToggle={() => toggleSection("match")}
        />

        <SentimentCard
          sentiment={result.sentiment}
          isExpanded={isSectionExpanded("sentiment")}
          onToggle={() => toggleSection("sentiment")}
        />
      </Stack>

      <Modal
        opened={showRawJson}
        onClose={() => setShowRawJson(false)}
        title="Raw JSON Response"
        size="xl"
      >
        <Code block style={{ maxHeight: "70vh", overflow: "auto" }}>
          {JSON.stringify(result, null, 2)}
        </Code>
      </Modal>
    </>
  );
}
