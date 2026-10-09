/** Shared data contract only: no database, session, or private profile records. */
export const INTAKE_VERSION = 1 as const;
export const READER_ROLES = [
  { value: 'clinician', label: 'Clinician/healthcare professional' },
  { value: 'general_reader', label: 'General reader/citizen' },
  { value: 'researcher', label: 'Researcher/academic' },
  { value: 'industry', label: 'Industry/professional' },
  { value: 'student', label: 'Student/trainee' },
  { value: 'other', label: 'Other' },
  { value: 'prefer_not_to_say', label: 'Prefer not to say' },
] as const;
export type ReaderRole = typeof READER_ROLES[number]['value'];
export type ReaderProfile = {
  userId: string;
  intakeVersion: typeof INTAKE_VERSION;
  roles: ReaderRole[];
  intakeState: 'complete' | 'declined';
  completedAt: string;
  updatedAt: string;
};
export type ProfileView = Omit<ReaderProfile, 'userId'>;
export function profileView(profile: ReaderProfile): ProfileView {
  return { intakeVersion: profile.intakeVersion, roles: [...profile.roles], intakeState: profile.intakeState,
    completedAt: profile.completedAt, updatedAt: profile.updatedAt };
}
export function hasCurrentIntake(profile: ReaderProfile | null, userId: string): boolean {
  if (!profile || profile.userId !== userId || profile.intakeVersion !== INTAKE_VERSION) return false;
  if (!Array.isArray(profile.roles) || !profile.roles.length || new Set(profile.roles).size !== profile.roles.length) return false;
  if (!profile.roles.every(role => READER_ROLES.some(option => option.value === role))) return false;
  const declined = profile.roles.includes('prefer_not_to_say');
  if (declined ? profile.roles.length !== 1 || profile.intakeState !== 'declined' : profile.intakeState !== 'complete') return false;
  return Number.isFinite(Date.parse(profile.completedAt)) && Number.isFinite(Date.parse(profile.updatedAt));
}
