import { Stack, Title, Text, Button } from "@mantine/core";
import Link from "next/link";

export default function NotFound() {
  return (
    <Stack align="center" gap="md" p="xl">
      <Title order={1}>Result Not Found</Title>
      <Text c="dimmed">
        The screening result you&apos;re looking for doesn&apos;t exist.
      </Text>
      <Button component={Link} href="/results">
        Back to Results
      </Button>
    </Stack>
  );
}
