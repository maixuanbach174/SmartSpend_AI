// app/account/[account_id]/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';

type Profile = {
  first_name: string;
  last_name: string;
  dob: string;
  email: string;
  account_id: number;
  country: string;
  gender: number;
  start_date: string;
};

export default function AccountProfile() {
  const { account_id } = useParams();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/account/${account_id}`);
        if (!res.ok) throw new Error('Failed to fetch profile');
        const json = await res.json();
        setProfile(json);
      } catch (err: any) {
        setError(err.message);
      }
    };

    fetchProfile();
  }, [account_id]);

  if (error) return <p style={{ color: 'red' }}>{error}</p>;
  if (!profile) return <p>Loading...</p>;

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Account Profile</h1>
      <p><strong>Name:</strong> {profile.first_name} {profile.last_name}</p>
      <p><strong>Email:</strong> {profile.email}</p>
      <p><strong>Date of Birth:</strong> {profile.dob}</p>
      <p><strong>Country:</strong> {profile.country}</p>
      <p><strong>Gender:</strong> {profile.gender === 0 ? 'Male' : 'Female'}</p>
      <p><strong>Account ID:</strong> {profile.account_id}</p>
      <p><strong>Start Date:</strong> {profile.start_date}</p>
    </div>
  );
}
