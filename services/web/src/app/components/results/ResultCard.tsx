"use client";

import { Card, Text, Stack } from "@mantine/core";
import Link from "next/link";
import type { ResultMetadata } from "~/types/results";

interface ResultCardProps {
  result: ResultMetadata;
}

// Config for date formatting
const DATE_FORMAT_OPTIONS: Intl.DateTimeFormatOptions = {
  year: "numeric",
  month: "short",
  day: "numeric",
  hour: "2-digit",
  minute: "2-digit",
};

export function ResultCard({ result }: ResultCardProps) {
  const formattedDate = new Date(result.created_at).toLocaleDateString(
    "en-US",
    DATE_FORMAT_OPTIONS,
  );

  return (
    <Card
      component={Link}
      href={`/results/${result.id}`}
      shadow="sm"
      padding="lg"
      radius="md"
      withBorder
      style={{
        cursor: "pointer",
        textDecoration: "none",
        color: "inherit",
        transition: "transform 0.2s, box-shadow 0.2s",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "translateY(-2px)";
        e.currentTarget.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.15)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.boxShadow = "";
      }}
    >
      <Stack gap="xs">
        <Text fw={600} size="lg">
          {result.person_name}
        </Text>
        <Text size="sm" c="dimmed" lineClamp={2}>
          {result.article_title}
        </Text>
        <Text size="xs" c="dimmed">
          {formattedDate}
        </Text>
      </Stack>
    </Card>
  );
}
