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
    let userFriendlyErr = 'Google OAuth failed (Error 500: Unconfigured Google Consent Screen / Firebase OAuth Client ID).';
    if (error.code === 'auth/operation-not-allowed') {
      userFriendlyErr = 'Google Provider is not enabled in Firebase Console (Authentication -> Sign-in method -> Google).';
    } else if (error.code === 'auth/unauthorized-domain') {
      userFriendlyErr = 'localhost is not added to Authorized Domains in Firebase Console Settings.';
    } else if (error.code === 'auth/popup-closed-by-user') {
      userFriendlyErr = 'Google Sign-In popup was closed before completing authentication.';
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
    let userFriendlyErr = 'GitHub OAuth failed (Unconfigured GitHub Client ID/Secret in Firebase Console).';
    if (error.code === 'auth/operation-not-allowed') {
      userFriendlyErr = 'GitHub Provider is not enabled in Firebase Console.';
    } else if (error.code === 'auth/popup-closed-by-user') {
      userFriendlyErr = 'GitHub Sign-In popup was closed before completing authentication.';
    }
    return {
      success: false,
      error: userFriendlyErr,
      code: error.code
    };
  }
};
