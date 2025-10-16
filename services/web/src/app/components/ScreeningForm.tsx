import { Button, Stack, TextInput, Select, Group, Text } from "@mantine/core";
import { useForm, Controller } from "react-hook-form";

export interface ScreeningFormData {
  url: string;
  firstName: string;
  lastName: string;
  middleNames?: string;
  birthDay?: number;
  birthMonth?: number;
  birthYear?: number;
}

interface ScreeningFormProps {
  onSubmit: (data: ScreeningFormData) => void;
  isLoading: boolean;
}

// Config: Month options for date picker
const MONTHS = [
  { value: "1", label: "January" },
  { value: "2", label: "February" },
  { value: "3", label: "March" },
  { value: "4", label: "April" },
  { value: "5", label: "May" },
  { value: "6", label: "June" },
  { value: "7", label: "July" },
  { value: "8", label: "August" },
  { value: "9", label: "September" },
  { value: "10", label: "October" },
  { value: "11", label: "November" },
  { value: "12", label: "December" },
];

// Config: Name input fields
const NAME_FIELDS = [
  { name: "firstName" as const, placeholder: "First name", required: true },
  {
    name: "middleNames" as const,
    placeholder: "Middle name(s) (optional)",
    required: false,
  },
  { name: "lastName" as const, placeholder: "Last name", required: true },
];

export function ScreeningForm({ onSubmit, isLoading }: ScreeningFormProps) {
  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<ScreeningFormData>();

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Stack gap="md">
        <TextInput
          {...register("url")}
          label="Article URL"
          placeholder="https://example.com/article"
          required
          error={errors.url?.message}
        />

        <div>
          <Text size="sm" fw={500} mb="xs">
            Person Name
          </Text>
          <Stack gap="xs">
            <Group grow>
              {NAME_FIELDS.map((field) => (
                <TextInput
                  key={field.name}
                  {...register(field.name)}
                  placeholder={field.placeholder}
                  required={field.required}
                  error={errors[field.name]?.message}
                />
              ))}
            </Group>
          </Stack>
        </div>

        <div>
          <Text size="sm" fw={500} mb="xs">
            Date of Birth (Optional)
          </Text>
          <Group grow>
            <Controller
              name="birthMonth"
              control={control}
              render={({ field }) => (
                <Select
                  {...field}
                  value={field.value?.toString()}
                  onChange={(value) =>
                    field.onChange(value ? Number(value) : undefined)
                  }
                  placeholder="Month"
                  data={MONTHS}
                  clearable
                  searchable
                />
              )}
            />
            <TextInput
              {...register("birthDay", { valueAsNumber: true })}
              placeholder="Day"
              type="number"
              // todo: make this dynamic based on the month and year (leap year)
              min={1}
              max={31}
            />
            <TextInput
              {...register("birthYear", { valueAsNumber: true })}
              placeholder="Year"
              type="number"
              // consider dropping the min and max
              min={1900}
              max={2030}
            />
          </Group>
        </div>

        <Button type="submit" loading={isLoading} fullWidth size="md">
          Screen Article
        </Button>
      </Stack>
    </form>
  );
}
