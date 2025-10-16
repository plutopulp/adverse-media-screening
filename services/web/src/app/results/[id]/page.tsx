import { Stack } from "@mantine/core";
import { notFound } from "next/navigation";
import { fetchResultById } from "~/lib/results-api";
import { ScreeningResultDisplay } from "~/app/components/ScreeningResultDisplay";

export default async function ResultDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  const result = await fetchResultById(id).catch(() => notFound());

  return (
    <Stack p="xl" maw={1200} mx="auto">
      <ScreeningResultDisplay result={result} />
    </Stack>
  );
}
