"use client";

import { Stack, Title } from "@mantine/core";
import { useState } from "react";
import { api } from "~/trpc/react";
import type { ScreeningResult } from "~/types/screening";
import { ScreeningResultDisplay } from "./components/ScreeningResultDisplay";
import {
  ScreeningForm,
  type ScreeningFormData,
} from "./components/ScreeningForm";

export default function Home() {
  const [result, setResult] = useState<ScreeningResult | null>(null);

  const checkWebsite = api.screening.checkWebsite.useMutation({
    onSuccess: (data) => {
      console.log(data);
      setResult(data);
    },
  });

  const handleSubmit = (formData: ScreeningFormData) => {
    checkWebsite.mutate({
      ...formData,
      birthDay: formData.birthDay ? Number(formData.birthDay) : undefined,
      birthMonth: formData.birthMonth ? Number(formData.birthMonth) : undefined,
      birthYear: formData.birthYear ? Number(formData.birthYear) : undefined,
    });
  };

  return (
    <Stack p="xl" maw={result ? 1200 : 600} mx="auto">
      {!result && <Title order={1}>New Screening</Title>}
      {result ? (
        <ScreeningResultDisplay result={result} />
      ) : (
        <ScreeningForm
          onSubmit={handleSubmit}
          isLoading={checkWebsite.isPending}
        />
      )}
    </Stack>
  );
}
