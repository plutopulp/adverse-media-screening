import { List, Text } from "@mantine/core";

interface EvidenceListProps {
  items: string[];
  title?: string;
  color?: string;
}

export function EvidenceList({
  items,
  title,
  color = "gray",
}: EvidenceListProps) {
  if (items.length === 0) return null;

  return (
    <div>
      {title && (
        <Text size="sm" fw={500} mb="xs" c={color}>
          {title}
        </Text>
      )}
      <List size="sm" spacing="xs">
        {items.map((item, index) => (
          <List.Item key={index}>{item}</List.Item>
        ))}
      </List>
    </div>
  );
}
