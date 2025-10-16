import { SimpleGrid, Stack, Title } from "@mantine/core";
import { fetchResultsList } from "~/lib/results-api";
import { ResultCard } from "~/app/components/results/ResultCard";
import { EmptyState } from "~/app/components/results/EmptyState";

export default async function ResultsPage() {
  const results = await fetchResultsList();

  return (
    <Stack p="xl" maw={1200} mx="auto">
      <Title order={1}>All Results</Title>

      {results.length === 0 ? (
        <EmptyState />
      ) : (
        <SimpleGrid cols={{ base: 1, sm: 2, md: 3 }} spacing="lg">
          {results.map((result) => (
            <ResultCard key={result.id} result={result} />
          ))}
        </SimpleGrid>
      )}
    </Stack>
  );
}
