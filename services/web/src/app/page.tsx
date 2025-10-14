"use client";

import { Button, Stack, TextInput, Title } from "@mantine/core";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { api } from "~/trpc/react";

export default function Home() {
  const [result, setResult] = useState<{
    match: boolean;
    sentiment: string;
  } | null>(null);
  const form = useForm<{ url: string; name: string; dateOfBirth: string }>();
  const checkWebsite = api.screening.checkWebsite.useMutation({
    onSuccess: (data) => {
      console.log(data);
      setResult(data);
    },
  });

  return (
    <Stack p="xl" maw={500} mx="auto">
      <Title order={1}>Screening tool</Title>
      {result ? (
        <Stack>
          <pre>{JSON.stringify(result, null, 2)}</pre>
          <Button onClick={() => setResult(null)}>Back</Button>
        </Stack>
      ) : (
        <form
          onSubmit={form.handleSubmit((v) => {
            checkWebsite.mutate(v);
          })}
        >
          <Stack gap="xs">
            <TextInput
              {...form.register("url")}
              label="URL"
              placeholder="https://example.com"
              required
            />
            <TextInput
              {...form.register("name")}
              label="Full name"
              placeholder="John Doe"
              required
            />
            <TextInput
              type="date"
              {...form.register("dateOfBirth")}
              label="Date of birth"
            />
            <Button type="submit" loading={checkWebsite.isPending}>
              Submit
            </Button>
          </Stack>
        </form>
      )}
    </Stack>
  );
}
