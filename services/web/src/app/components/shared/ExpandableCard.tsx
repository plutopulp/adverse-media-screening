import { Card, Stack, Group, Text, Button, Collapse } from "@mantine/core";
import type { ReactNode } from "react";

interface ExpandableCardProps {
  title: string;
  children: ReactNode;
  badge?: ReactNode;
  isExpanded: boolean;
  onToggle: () => void;
  defaultContent?: ReactNode;
}

export function ExpandableCard({
  title,
  children,
  badge,
  isExpanded,
  onToggle,
  defaultContent,
}: ExpandableCardProps) {
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Stack gap="md">
        <Group justify="space-between">
          <Group gap="sm">
            <Text fw={600} size="lg">
              {title}
            </Text>
            {badge}
          </Group>
          <Button
            variant="subtle"
            size="compact-sm"
            onClick={onToggle}
            aria-label={isExpanded ? "Collapse" : "Expand"}
          >
            {isExpanded ? "▲ Hide" : "▼ Show Details"}
          </Button>
        </Group>

        {defaultContent && !isExpanded && defaultContent}

        <Collapse in={isExpanded}>{children}</Collapse>
      </Stack>
    </Card>
  );
}
