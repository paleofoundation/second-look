CREATE TABLE `corrections` (
	`id` text PRIMARY KEY NOT NULL,
	`user_id` text NOT NULL,
	`page` text NOT NULL,
	`message` text NOT NULL,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `saved_items` (
	`user_id` text NOT NULL,
	`item_id` text NOT NULL,
	`note` text DEFAULT '' NOT NULL,
	`updated_at` text NOT NULL,
	PRIMARY KEY(`user_id`, `item_id`)
);
