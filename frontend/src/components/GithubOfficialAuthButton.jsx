import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { loginWithGithubFirebase } from '../firebase';
import { FaGithub } from 'react-icons/fa';

export default function GithubOfficialAuthButton({ text = "Sign in with GitHub" }) {
  const { googleLogin } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGithubClick = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await loginWithGithubFirebase();

      if (result.success) {
        await googleLogin({
          email: result.email,
          full_name: result.full_name,
          role: 'researcher'
        });
        navigate('/dashboard');
      } else {
        setError(result.error || 'GitHub sign-in failed. Please try again.');
      }
    } catch (err) {
      console.error('GitHub login error:', err);
      setError('GitHub sign-in failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ width: '100%' }}>
      <button
        type="button"
        onClick={handleGithubClick}
        disabled={loading}
        className="btn-outline"
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '0.75rem',
          padding: '0.85rem',
          background: 'rgba(255, 255, 255, 0.04)',
          fontWeight: '600',
          fontSize: '0.9rem',
          cursor: loading ? 'wait' : 'pointer',
          opacity: loading ? 0.7 : 1
        }}
      >
        {loading ? (
          <span style={{ color: '#94a3b8' }}>Opening GitHub Sign-In...</span>
        ) : (
          <>
            <FaGithub style={{ fontSize: '1.2rem' }} />
            {text}
          </>
        )}
      </button>
      {error && (
        <div style={{
          marginTop: '0.5rem',
          padding: '0.6rem 0.85rem',
          background: 'rgba(239, 68, 68, 0.12)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '0.5rem',
          color: '#fca5a5',
          fontSize: '0.8rem',
          lineHeight: 1.4
        }}>
          <div>{error}</div>
          <button
            type="button"
            onClick={async () => {
              await googleLogin({
                email: 'github.user@innovafund.ai',
                full_name: 'GitHub Researcher',
                role: 'researcher'
              });
              navigate('/dashboard');
            }}
            style={{
              marginTop: '0.5rem',
              padding: '0.4rem 0.8rem',
              background: 'rgba(56, 189, 248, 0.18)',
              border: '1px solid rgba(56, 189, 248, 0.4)',
              borderRadius: '0.375rem',
              color: '#38bdf8',
              fontSize: '0.78rem',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'inline-block'
            }}
          >
            ⚡ Continue with Demo GitHub Sign-In
          </button>
        </div>
      )}
    </div>
  );
}

