CREATE TABLE `reader_profiles` (
	`user_id` text PRIMARY KEY NOT NULL,
	`intake_version` integer NOT NULL,
	`roles_json` text NOT NULL,
	`intake_state` text NOT NULL,
	`completed_at` text NOT NULL,
	`updated_at` text NOT NULL
);
