import { useState } from "react";

export function useScreeningResult() {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(),
  );
  const [showRawJson, setShowRawJson] = useState(false);

  const toggleSection = (id: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const isSectionExpanded = (id: string) => {
    return expandedSections.has(id);
  };

  const expandAll = () => {
    setExpandedSections(
      new Set(["article", "match", "sentiment", "credibility"]),
    );
  };

  const collapseAll = () => {
    setExpandedSections(new Set());
  };

  return {
    expandedSections,
    showRawJson,
    toggleSection,
    isSectionExpanded,
    setShowRawJson,
    expandAll,
    collapseAll,
  };
}
