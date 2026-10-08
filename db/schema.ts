import { sqliteTable, text, primaryKey } from 'drizzle-orm/sqlite-core';
export const savedItems=sqliteTable('saved_items',{userId:text('user_id').notNull(),itemId:text('item_id').notNull(),note:text('note').notNull().default(''),updatedAt:text('updated_at').notNull() },t=>[primaryKey({columns:[t.userId,t.itemId]})]);
export const corrections=sqliteTable('corrections',{id:text('id').primaryKey(),userId:text('user_id').notNull(),page:text('page').notNull(),message:text('message').notNull(),createdAt:text('created_at').notNull()});
