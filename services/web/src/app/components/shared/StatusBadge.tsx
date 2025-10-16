import { Badge } from "@mantine/core";
import type { MantineColor } from "~/lib/screening-utils";

interface StatusBadgeProps {
  label: string;
  color: MantineColor;
  variant?: "filled" | "light" | "outline";
  size?: "sm" | "md" | "lg";
}

export function StatusBadge({
  label,
  color,
  variant = "light",
  size = "md",
}: StatusBadgeProps) {
  return (
    <Badge color={color} variant={variant} size={size}>
      {label}
    </Badge>
  );
}
