import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getStorage } from "firebase/storage";

// Web App Config (Placeholder - will update with real config from project)
const firebaseConfig = {
  // Using placeholders. In a real scenario, we'd fetch these from the Firebase Console.
  // For now, since we are hosting ON Firebase, the automatic init usually works,
  // but explicit config is safer for local dev.
  apiKey: "AIzaSyAQReDH4oXNrwITcXbSz7eFwfxA46u7YJE", // Using the key provided earlier
  authDomain: "kintsu-gcp.firebaseapp.com",
  projectId: "kintsu-gcp",
  storageBucket: "kintsu-hopper-kintsu-gcp",
  messagingSenderId: "351476623210",
  appId: "1:351476623210:web:aca6e03378943805" // Placeholder App ID
};

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
export const storage = getStorage(app);
