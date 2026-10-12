import { INTAKE_VERSION, READER_ROLES, hasCurrentIntake, type ReaderRole, type ReaderProfile } from './account-contract';
import { topicGuideMappings } from './topic-guides';
export type ProfileStatement = {
  bind(...values: (string | number | null)[]): ProfileStatement;
  first<T>(): Promise<T | null>;
  run(): Promise<unknown>;
};
export type ProfileDatabase = { prepare(sql: string): ProfileStatement };
export class ProfileInputError extends Error {}
export function validateRolesInput(value: unknown): ReaderRole[] {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).some(key => !['roles', 'interests'].includes(key))) throw new ProfileInputError('Choose only your reader roles and listed topics.');
  const roles = (value as { roles?: unknown }).roles;
  if (!Array.isArray(roles) || !roles.length || roles.length > READER_ROLES.length || new Set(roles).size !== roles.length || !roles.every(role => typeof role === 'string' && READER_ROLES.some(option => option.value === role))) throw new ProfileInputError('Select at least one of the listed roles.');
  if (roles.includes('prefer_not_to_say') && roles.length !== 1) throw new ProfileInputError('Prefer not to say must be selected on its own.');
  // Stable order keeps exports deterministic; order does not encode status or privileges.
  return READER_ROLES.map(option => option.value).filter(role => roles.includes(role));
}
export function validateInterestsInput(value: unknown): string[] {
  const known = new Set(topicGuideMappings.map(topic => `${topic.kind}:${topic.slug}`));
  if (!Array.isArray(value) || value.length > known.size || new Set(value).size !== value.length || !value.every(item => typeof item === 'string' && known.has(item))) throw new ProfileInputError('Choose topics from the drug and condition list, or leave interests empty.');
  return [...value].sort();
}
type Row = { user_id: string; intake_version: number; roles_json: string; interests_json?: string; intake_state: string; completed_at: string; updated_at: string };
export function createProfileRepository(db: ProfileDatabase, now = () => new Date().toISOString()) {
  async function read(userId: string): Promise<ReaderProfile | null> {
    const row = await db.prepare('SELECT user_id, intake_version, roles_json, interests_json, intake_state, completed_at, updated_at FROM reader_profiles WHERE user_id = ?').bind(userId).first<Row>();
    if (!row) return null;
    // Old/future schema records require a current intake; they never grant access.
    if (row.intake_version !== INTAKE_VERSION) return null;
    const storedInterests: unknown = JSON.parse(row.interests_json ?? '[]');
    if (!Array.isArray(storedInterests) || !storedInterests.every(item => typeof item === 'string')) throw new Error('Invalid stored interests');
    const profile = { userId: row.user_id, intakeVersion: row.intake_version, roles: JSON.parse(row.roles_json), interests: storedInterests, intakeState: row.intake_state, completedAt: row.completed_at, updatedAt: row.updated_at } as ReaderProfile;
    if (!hasCurrentIntake(profile, userId)) throw new Error('Invalid stored profile');
    return profile;
  }
  return {
    read,
    async save(userId: string, input: unknown): Promise<ReaderProfile> {
      const roles = validateRolesInput(input);
      const hasInterests = Object.prototype.hasOwnProperty.call(input, 'interests');
      const interests = hasInterests ? validateInterestsInput((input as { interests: unknown }).interests) : [];
      const at = now();
      const state = roles.includes('prefer_not_to_say') ? 'declined' : 'complete';
      // The database owns completion/identity. Upsert preserves the first valid completion
      // timestamp for this schema version, including concurrent first-login submissions.
      const result = await db.prepare(`INSERT INTO reader_profiles (user_id, intake_version, roles_json, intake_state, completed_at, updated_at, interests_json)
        VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET
        intake_version=excluded.intake_version, roles_json=excluded.roles_json, intake_state=excluded.intake_state,
        completed_at=CASE WHEN reader_profiles.intake_version=excluded.intake_version THEN reader_profiles.completed_at ELSE excluded.completed_at END,
        updated_at=excluded.updated_at,
        interests_json=CASE WHEN ? = 1 THEN excluded.interests_json ELSE reader_profiles.interests_json END`).bind(userId, INTAKE_VERSION, JSON.stringify(roles), state, at, at, JSON.stringify(interests), hasInterests ? 1 : 0).run();
      if (result && typeof result === 'object' && 'success' in result && result.success === false) throw new Error('Profile write failed');
      const profile = await read(userId);
      if (!profile) throw new Error('Profile readback failed');
      return profile;
    },
    async remove(userId: string): Promise<void> {
      const result = await db.prepare('DELETE FROM reader_profiles WHERE user_id = ?').bind(userId).run();
      if (result && typeof result === 'object' && 'success' in result && result.success === false) throw new Error('Profile deletion failed');
    },
  };
}
export type ProfileRepository = ReturnType<typeof createProfileRepository>;
