/**
 * TypeScript types for screening results persistence.
 *
 * Manually mapped from Python Pydantic models.
 */

export interface ResultMetadata {
  id: string;
  display_name: string;
  person_name: string;
  article_url: string;
  article_title: string;
  created_at: string;
  schema_version: string;
}
