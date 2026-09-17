import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, GithubAuthProvider, signInWithPopup } from 'firebase/auth';

// Official Firebase Credentials (innovafundai)
const firebaseConfig = {
  apiKey: "AIzaSyC_DtS2NOy3GEE7ymQ8g8z1XAMtCtDgf2o",
  authDomain: "innovafundai.firebaseapp.com",
  projectId: "innovafundai",
  storageBucket: "innovafundai.firebasestorage.app",
  messagingSenderId: "1052740463420",
  appId: "1:1052740463420:web:b857e21b5ef703fbe18c39",
  measurementId: "G-2CW5MLPLZ3"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({ prompt: 'select_account' });

export const githubProvider = new GithubAuthProvider();
githubProvider.setCustomParameters({ prompt: 'consent' });

export const loginWithGoogleFirebase = async () => {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    const user = result.user;
    return {
      success: true,
      email: user.email,
      full_name: user.displayName || (user.email ? user.email.split('@')[0] : 'Google User'),
      photoURL: user.photoURL,
      uid: user.uid
    };
  } catch (error) {
    console.error('Firebase Google Auth error:', error);
    let userFriendlyErr = error.message || 'Google sign-in failed.';
    if (error.code === 'auth/popup-blocked') {
      userFriendlyErr = 'Google Sign-In popup was blocked by your browser. Please allow popups for this site in your address bar, or use Quick Demo Sign-In below.';
    } else if (error.code === 'auth/popup-closed-by-user') {
      userFriendlyErr = 'Google Sign-In popup was closed before completing authentication.';
    } else if (error.code === 'auth/cancelled-popup-request') {
      userFriendlyErr = 'Multiple popup requests detected. Please try again.';
    } else if (error.code === 'auth/operation-not-allowed') {
      userFriendlyErr = 'Google Provider is not enabled in Firebase Console.';
    } else if (error.code === 'auth/unauthorized-domain') {
      userFriendlyErr = 'This domain is not in the Firebase Authorized Domains list.';
    } else if (error.code === 'auth/network-request-failed') {
      userFriendlyErr = 'Network error: could not connect to Google authentication server.';
    }
    return {
      success: false,
      error: userFriendlyErr,
      code: error.code
    };
  }
};

export const loginWithGithubFirebase = async () => {
  try {
    const result = await signInWithPopup(auth, githubProvider);
    const user = result.user;
    return {
      success: true,
      email: user.email || 'user@innovafund.ai',
      full_name: user.displayName || (user.email ? user.email.split('@')[0] : 'GitHub User'),
      photoURL: user.photoURL,
      uid: user.uid
    };
  } catch (error) {
    console.error('Firebase GitHub Auth error:', error);
    let userFriendlyErr = error.message || 'GitHub sign-in failed.';
    if (error.code === 'auth/popup-blocked') {
      userFriendlyErr = 'GitHub Sign-In popup was blocked by your browser. Please allow popups for this site in your address bar, or use Quick Demo Sign-In below.';
    } else if (error.code === 'auth/popup-closed-by-user') {
      userFriendlyErr = 'GitHub Sign-In popup was closed before completing authentication.';
    } else if (error.code === 'auth/cancelled-popup-request') {
      userFriendlyErr = 'Multiple popup requests detected. Please try again.';
    } else if (error.code === 'auth/operation-not-allowed') {
      userFriendlyErr = 'GitHub Provider is not enabled in Firebase Console.';
    } else if (error.code === 'auth/unauthorized-domain') {
      userFriendlyErr = 'This domain is not in the Firebase Authorized Domains list.';
    } else if (error.code === 'auth/network-request-failed') {
      userFriendlyErr = 'Network error: could not connect to GitHub authentication server.';
    }
    return {
      success: false,
      error: userFriendlyErr,
      code: error.code
    };
  }
};
