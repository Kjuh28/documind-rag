-- Create "concept_reviews" table
CREATE TABLE `concept_reviews` (
  `id` integer NOT NULL,
  `term` varchar NOT NULL,
  `context` varchar NOT NULL,
  `translation` varchar NULL,
  `synonyms` varchar NULL,
  `review_stage` integer NULL,
  `next_review_date` datetime NULL,
  `created_at` datetime NULL,
  `updated_at` datetime NULL,
  PRIMARY KEY (`id`)
);
-- Create index "ix_concept_reviews_term" to table: "concept_reviews"
CREATE INDEX `ix_concept_reviews_term` ON `concept_reviews` (`term`);
-- Create index "ix_concept_reviews_id" to table: "concept_reviews"
CREATE INDEX `ix_concept_reviews_id` ON `concept_reviews` (`id`);
