import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { loginWithGithubFirebase } from '../firebase';
import { FaGithub } from 'react-icons/fa';

export default function GithubOfficialAuthButton({ text = "Sign in with GitHub", onError }) {
  const { googleLogin } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleGithubClick = async () => {
    setLoading(true);
    try {
      const githubUser = await loginWithGithubFirebase();
      if (githubUser && githubUser.success) {
        await googleLogin({
          email: githubUser.email,
          full_name: githubUser.full_name,
          role: 'researcher'
        });
        navigate('/dashboard');
      } else {
        const errMsg = githubUser?.error || 'GitHub OAuth failed (Unconfigured OAuth App Client ID/Secret).';
        if (onError) {
          onError(`GitHub Auth Error: ${errMsg} Click 'Quick Demo Sign-In' below to test the portal without OAuth.`);
        }
      }
    } catch (err) {
      console.error('GitHub login catch error:', err);
      if (onError) {
        onError(`GitHub Sign-In failed: ${err.message || 'Error from GitHub Provider'}. Use Quick Demo Sign-In below.`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      type="button"
      onClick={handleGithubClick}
      disabled={loading}
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
        cursor: loading ? 'not-allowed' : 'pointer'
      }}
    >
      <FaGithub style={{ fontSize: '1.2rem' }} />
      {loading ? 'Authenticating GitHub...' : text}
    </button>
  );
}
