"use client";

import { Stack, Title, Group, Switch } from "@mantine/core";
import { useState, useEffect, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { api } from "~/trpc/react";
import type { ScreeningResult } from "~/types/screening";
import { ScreeningResultDisplay } from "./components/ScreeningResultDisplay";
import {
  ScreeningForm,
  type ScreeningFormData,
} from "./components/ScreeningForm";

// Hook: Manage mock mode state synced with URL query param
function useMockMode() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [useMockData, setUseMockData] = useState(false);

  // Initialize from URL param
  useEffect(() => {
    const mockParam = searchParams.get("mock");
    if (mockParam === "true") {
      setUseMockData(true);
    }
  }, [searchParams]);

  // Toggle mock mode and update URL
  const toggleMockMode = useCallback(
    (checked: boolean) => {
      setUseMockData(checked);
      const url = new URL(window.location.href);
      if (checked) {
        url.searchParams.set("mock", "true");
      } else {
        url.searchParams.delete("mock");
      }
      router.replace(url.pathname + url.search);
    },
    [router],
  );

  return { useMockData, toggleMockMode };
}

// Hook: Manage screening data fetching and results
function useScreening(useMockData: boolean) {
  const [result, setResult] = useState<ScreeningResult | null>(null);

  const checkWebsite = api.screening.checkWebsite.useMutation({
    onSuccess: (data) => {
      console.log(data);
      setResult(data);
    },
  });

  // Load mock data from test endpoint
  const loadMockData = useCallback(async () => {
    try {
      const mockUrl = `http://localhost:5001/test/mock-result?example=roman-typo-2`;
      const response = await fetch(mockUrl);
      const data = (await response.json()) as ScreeningResult;
      setResult(data);
    } catch (error) {
      console.error("Failed to load mock data:", error);
    }
  }, []);

  // Submit form (either mock or real screening)
  const handleSubmit = useCallback(
    (formData: ScreeningFormData) => {
      if (useMockData) {
        void loadMockData();
      } else {
        checkWebsite.mutate({
          ...formData,
          birthDay: formData.birthDay ? Number(formData.birthDay) : undefined,
          birthMonth: formData.birthMonth
            ? Number(formData.birthMonth)
            : undefined,
          birthYear: formData.birthYear
            ? Number(formData.birthYear)
            : undefined,
        });
      }
    },
    [useMockData, loadMockData, checkWebsite],
  );

  // Reset to new search
  const resetResult = useCallback(() => {
    setResult(null);
  }, []);

  return {
    result,
    isLoading: checkWebsite.isPending,
    handleSubmit,
    resetResult,
  };
}

export default function Home() {
  const { useMockData, toggleMockMode } = useMockMode();
  const { result, isLoading, handleSubmit, resetResult } =
    useScreening(useMockData);

  return (
    <Stack p="xl" maw={result ? 1200 : 600} mx="auto">
      <Group justify="space-between" align="center">
        <Title order={1}>Adverse Media Screening Tool</Title>
        {!result && (
          <Switch
            label="Use Mock Data (Dev Mode)"
            checked={useMockData}
            onChange={(event) => toggleMockMode(event.currentTarget.checked)}
          />
        )}
      </Group>
      {result ? (
        <ScreeningResultDisplay result={result} onNewSearch={resetResult} />
      ) : (
        <ScreeningForm
          onSubmit={handleSubmit}
          isLoading={isLoading}
          useMockData={useMockData}
        />
      )}
    </Stack>
  );
}
