import { getChatGPTUser } from '@/app/chatgpt-auth';
import { readerProfiles } from '@/lib/profile-server';
import { createProfileHandlers } from '@/lib/profile-api';
export const dynamic = 'force-dynamic';
const handlers = createProfileHandlers({ getUser: getChatGPTUser, repository: readerProfiles });
export const GET = handlers.GET;
export const PUT = handlers.PUT;
export const DELETE = handlers.DELETE;
