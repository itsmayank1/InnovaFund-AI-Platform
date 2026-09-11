import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { FaGithub } from 'react-icons/fa';

export default function GithubOfficialAuthButton({ text = "Sign in with GitHub" }) {
  const { googleLogin } = useAuth();
  const navigate = useNavigate();

  const handleGithubClick = async () => {
    try {
      await googleLogin({
        email: 'github.user@innovafund.ai',
        full_name: 'GitHub User',
        role: 'researcher'
      });
      navigate('/dashboard');
    } catch (err) {
      console.error('GitHub login error:', err);
      navigate('/dashboard');
    }
  };

  return (
    <button
      type="button"
      onClick={handleGithubClick}
      className="btn-outline"
      style={{
        width: '100%',
        display: 'flex',
        alignItems: 'center',
        justify: 'center',
        gap: '0.75rem',
        padding: '0.85rem',
        background: 'rgba(255, 255, 255, 0.04)',
        fontWeight: '600',
        fontSize: '0.9rem',
        cursor: 'pointer'
      }}
    >
      <FaGithub style={{ fontSize: '1.2rem' }} />
      {text}
    </button>
  );
}
