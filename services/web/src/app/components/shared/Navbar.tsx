import { Group, Button, Title } from "@mantine/core";
import Link from "next/link";

export function Navbar() {
  return (
    <Group
      justify="space-between"
      p="md"
      style={{
        borderBottom: "1px solid var(--mantine-color-gray-3)",
        backgroundColor: "var(--mantine-color-body)",
      }}
    >
      <Title order={3}>Adverse Media Screening</Title>
      <Group gap="sm">
        <Button component={Link} href="/" variant="subtle">
          New Screening
        </Button>
        <Button component={Link} href="/results" variant="subtle">
          View Results
        </Button>
      </Group>
    </Group>
  );
}
