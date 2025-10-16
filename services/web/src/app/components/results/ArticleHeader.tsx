import { Card, Stack, Group, Text, Anchor } from "@mantine/core";
import type { Article, CredibilityResult } from "~/types/screening";
import { StatusBadge } from "../shared/StatusBadge";
import {
  getCredibilityColor,
  getCredibilityLabel,
  formatScore,
} from "~/lib/screening-utils";

interface ArticleHeaderProps {
  article: Article;
  credibility: CredibilityResult | null;
}

export function ArticleHeader({ article, credibility }: ArticleHeaderProps) {
  const credibilityAssessment = credibility?.assessment;

  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Stack gap="sm">
        <Group justify="space-between" align="flex-start">
          <div style={{ flex: 1 }}>
            <Text fw={600} size="xl" mb="xs">
              📰 {article.title}
            </Text>
            <Anchor
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              size="sm"
            >
              {article.url}
            </Anchor>
          </div>
          {credibilityAssessment && (
            <StatusBadge
              label={`${getCredibilityLabel(credibilityAssessment.recommendation)} (${formatScore(credibilityAssessment.credibility_score)})`}
              color={getCredibilityColor(credibilityAssessment.recommendation)}
              size="lg"
            />
          )}
        </Group>

        {credibilityAssessment && (
          <Text size="sm" c="dimmed">
            {credibilityAssessment.rationale}
          </Text>
        )}
      </Stack>
    </Card>
  );
}
