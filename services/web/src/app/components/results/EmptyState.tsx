import { Stack, Text } from "@mantine/core";

export function EmptyState() {
  return (
    <Stack align="center" gap="md" py="xl">
      <Text size="lg" c="dimmed">
        No screening results yet
      </Text>
      <Text size="sm" c="dimmed">
        Use the &ldquo;New Screening&rdquo; button above to get started
      </Text>
    </Stack>
  );
}
